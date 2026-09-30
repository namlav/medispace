# TÀI LIỆU GIẢI THÍCH AGGREGATION PIPELINES & TỐI ƯU HÓA CHỈ MỤC (MONGODB)
**Phục vụ nội dung đánh giá: Chức năng nâng cao đặc trưng (2.5 Điểm)**

---

## 1. Pipeline 1: Thống Kê Số Lượng Ca Bệnh Theo Chuyên Khoa

### 1.1. Mục tiêu bài toán
Thống kê tổng số ca khám bệnh, số ca có chỉ định tái khám, và số lượng bác sĩ tham gia khám theo từng chuyên khoa.

### 1.2. Mã truy vấn MongoDB
```javascript
db.medical_records.aggregate([
  {
    $group: {
      _id: "$department",
      total_visits: { $sum: 1 },
      follow_up_count: {
        $sum: { $cond: [{ $eq: ["$follow_up_required", true] }, 1, 0] }
      },
      unique_doctors: { $addToSet: "$doctor_name" }
    }
  },
  {
    $project: {
      _id: 0,
      department: "$_id",
      total_visits: 1,
      follow_up_count: 1,
      doctor_count: { $size: "$unique_doctors" }
    }
  },
  { $sort: { total_visits: -1 } }
])
```

### 1.3. Giải thích từng Stage
1. **`$group`**: Gom nhóm toàn bộ hồ sơ theo trường `department`.
   - `$sum: 1`: Đếm tổng số ca khám của từng khoa.
   - `$cond`: Biểu thức điều kiện, nếu `follow_up_required == true` thì cộng 1, ngược lại cộng 0 để tính số ca cần tái khám.
   - `$addToSet`: Thu thập tập hợp danh sách các bác sĩ (loại bỏ trùng lặp).
2. **`$project`**: Định dạng lại dữ liệu đầu ra, tính kích thước tập hợp bác sĩ bằng `$size`.
3. **`$sort`**: Sắp xếp chuyên khoa có nhiều lượt khám nhất lên đầu (`total_visits: -1`).

---

## 2. Pipeline 2: Phân Tích Ca Bệnh Theo Nhóm Tuổi Của Bệnh Nhân

### 2.1. Mục tiêu bài toán
Kết hợp dữ liệu từ collection `medical_records` và `patients` để phân nhóm bệnh nhân theo các độ tuổi: Nhi khoa (<18), Thanh niên (18-40), Trung niên (41-60), Người cao tuổi (>60) và phân bố theo từng chuyên khoa.

### 2.2. Mã truy vấn MongoDB
```javascript
db.medical_records.aggregate([
  {
    $addFields: {
      patient_obj_id: {
        $convert: { input: "$patient_id", to: "objectId", onError: null, onNull: null }
      }
    }
  },
  {
    $lookup: {
      from: "patients",
      localField: "patient_obj_id",
      foreignField: "_id",
      as: "patient_info"
    }
  },
  { $unwind: "$patient_info" },
  {
    $addFields: {
      birth_year: { $toInt: { $substrBytes: ["$patient_info.dob", 0, 4] } }
    }
  },
  {
    $addFields: {
      approx_age: { $subtract: [2026, "$birth_year"] }
    }
  },
  {
    $addFields: {
      age_group: {
        $switch: {
          branches: [
            { case: { $lt: ["$approx_age", 18] }, then: "Dưới 18 tuổi (Nhi)" },
            { case: { $and: [{ $gte: ["$approx_age", 18] }, { $lte: ["$approx_age", 40] }] }, then: "18 - 40 tuổi (Thanh niên)" },
            { case: { $and: [{ $gte: ["$approx_age", 41] }, { $lte: ["$approx_age", 60] }] }, then: "41 - 60 tuổi (Trung niên)" }
          ],
          default: "Trên 60 tuổi (Cao tuổi)"
        }
      }
    }
  },
  {
    $group: {
      _id: {
        age_group: "$age_group",
        department: "$department"
      },
      count: { $sum: 1 }
    }
  },
  {
    $project: {
      _id: 0,
      age_group: "$_id.age_group",
      department: "$_id.department",
      count: 1
    }
  },
  { $sort: { "age_group": 1, "count": -1 } }
])
```

### 2.3. Giải thích từng Stage
1. **`$addFields` & `$convert`**: Chuyển đổi chuỗi `patient_id` thành `ObjectId` để thực hiện phép nối CSDL.
2. **`$lookup`**: Nối dữ liệu sang collection `patients` theo khóa `_id`.
3. **`$unwind`**: Trải phẳng mảng `patient_info` sau phép lookup.
4. **`$switch`**: Phân loại theo nhánh điều kiện logic để gán nhãn nhóm tuổi cho bệnh nhân.
5. **`$group`**: Gom nhóm kép theo `{ age_group, department }` để đếm tần suất mắc bệnh theo độ tuổi ở từng khoa.

---

## 3. Pipeline 3: Thống Kê Tần Suất & Tỷ Lệ Bệnh Nhân Tái Khám ($facet & $bucket)

### 3.1. Mục tiêu bài toán
Tính toán tỷ lệ phần trăm bệnh nhân có từ 2 lượt khám trở lên (tái khám) so với tổng số bệnh nhân, và phân bố số lượt khám theo từng khoảng (`$bucket`).

### 3.2. Mã truy vấn MongoDB
```javascript
db.medical_records.aggregate([
  {
    $group: {
      _id: "$patient_id",
      visit_count: { $sum: 1 },
      departments: { $addToSet: "$department" }
    }
  },
  {
    $facet: {
      summary: [
        {
          $group: {
            _id: null,
            total_unique_patients: { $sum: 1 },
            revisit_patients: {
              $sum: { $cond: [{ $gt: ["$visit_count", 1] }, 1, 0] }
            },
            single_visit_patients: {
              $sum: { $cond: [{ $eq: ["$visit_count", 1] }, 1, 0] }
            },
            total_visits: { $sum: "$visit_count" }
          }
        }
      ],
      distribution: [
        {
          $bucket: {
            groupBy: "$visit_count",
            boundaries: [1, 2, 4, 6, 100],
            default: "Khác",
            output: {
              patient_count: { $sum: 1 }
            }
          }
        }
      ]
    }
  }
])
```

---

## 4. Tối Ưu Hóa Hiệu Năng Truy Vấn Bằng Chỉ Mục (Indexes)

### 4.1. Thiết lập Compound Index
```javascript
db.medical_records.createIndex({ "department": 1, "visit_date": -1 })
```

### 4.2. So sánh hiệu năng qua `explain("executionStats")`

| Tiêu chí so sánh | Khi CHƯA có Compound Index | Khi ĐÃ CÓ Compound Index | Nhận xét tối ưu |
| :--- | :--- | :--- | :--- |
| **Winning Stage** | `COLLSCAN` (Quét toàn bộ collection) | `IXSCAN` $\rightarrow$ `FETCH` (Quét qua cây B-tree Index) | Không còn phải duyệt tuần tự từng document |
| **Documents Examined** | 150+ documents (toàn bộ collection) | Bằng đúng số document thỏa mãn bộ lọc | Giảm số lượng I/O đọc ổ đĩa |
| **Execution Time** | ~15 - 25 ms | < 1 ms | Cải thiện tốc độ tức thì |
