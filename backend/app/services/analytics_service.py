from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.app.core.config import settings
from backend.app.core.database import get_records_collection


class AnalyticsService:
    """Các Aggregation Pipeline phục vụ thống kê y tế (SV2).

    Toàn bộ phép đếm, gom nhóm và tính tỷ lệ đều diễn ra trong MongoDB;
    Python chỉ nhận kết quả cuối cùng.
    """

    @staticmethod
    def get_department_stats(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Pipeline 1: thống kê ca khám theo chuyên khoa.

        Stages: $match (khoảng visit_date) -> $group (theo department) -> $project -> $sort.
        `revisit_cases` đếm ca có chỉ định tái khám (follow_up_required).
        """
        col = get_records_collection()

        pipeline: List[Dict[str, Any]] = []
        visit_range = {}
        if start_date:
            visit_range["$gte"] = start_date
        if end_date:
            visit_range["$lte"] = end_date
        if visit_range:
            pipeline.append({"$match": {"visit_date": visit_range}})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$department",
                        "total_cases": {"$sum": 1},
                        "revisit_cases": {
                            "$sum": {"$cond": [{"$eq": ["$follow_up_required", True]}, 1, 0]}
                        },
                        "total_prescriptions": {
                            "$sum": {"$size": {"$ifNull": ["$prescriptions", []]}}
                        },
                        "unique_doctors": {"$addToSet": "$doctor_name"},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "department": "$_id",
                        "total_cases": 1,
                        "revisit_cases": 1,
                        "total_prescriptions": 1,
                        "doctor_count": {"$size": "$unique_doctors"},
                        # Giữ tên cũ để trang Streamlit của SV3 không phải sửa.
                        "total_visits": "$total_cases",
                        "follow_up_count": "$revisit_cases",
                    }
                },
                {"$sort": {"total_cases": -1}},
            ]
        )

        return list(col.aggregate(pipeline))

    @staticmethod
    def get_age_group_distribution() -> List[Dict[str, Any]]:
        """Pipeline 2: phân bố ca bệnh theo nhóm tuổi (0-18, 19-40, 41-60, 60+).

        Stages: $lookup + $unwind (nối patients) -> tính tuổi theo visit_date
        -> $switch (gán nhóm) -> $group -> $setWindowFields (tổng theo nhóm) -> $project (tỷ lệ %).
        """
        col = get_records_collection()

        pipeline = [
            {
                "$addFields": {
                    "patient_obj_id": {
                        "$convert": {
                            "input": "$patient_id",
                            "to": "objectId",
                            "onError": None,
                            "onNull": None,
                        }
                    }
                }
            },
            {
                "$lookup": {
                    "from": settings.PATIENTS_COLLECTION,
                    "localField": "patient_obj_id",
                    "foreignField": "_id",
                    "as": "patient_info",
                }
            },
            {"$unwind": "$patient_info"},
            {
                "$addFields": {
                    "birth_date": {
                        "$dateFromString": {
                            "dateString": "$patient_info.dob",
                            "onError": None,
                            "onNull": None,
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "age": {
                        "$dateDiff": {
                            "startDate": "$birth_date",
                            "endDate": "$visit_date",
                            "unit": "year",
                        }
                    }
                }
            },
            # Bỏ hồ sơ không xác định được ngày sinh để không tạo nhóm tuổi rác.
            {"$match": {"age": {"$gte": 0}}},
            {
                "$addFields": {
                    "age_group": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lte": ["$age", 18]}, "then": "0-18"},
                                {"case": {"$lte": ["$age", 40]}, "then": "19-40"},
                                {"case": {"$lte": ["$age", 60]}, "then": "41-60"},
                            ],
                            "default": "60+",
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {"age_group": "$age_group", "department": "$department"},
                    "count": {"$sum": 1},
                }
            },
            {
                "$setWindowFields": {
                    "partitionBy": "$_id.age_group",
                    "output": {"age_group_total": {"$sum": "$count"}},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "age_group": "$_id.age_group",
                    "department": "$_id.department",
                    "count": 1,
                    "percentage": {
                        "$round": [
                            {"$multiply": [{"$divide": ["$count", "$age_group_total"]}, 100]},
                            2,
                        ]
                    },
                }
            },
            {"$sort": {"age_group": 1, "count": -1}},
        ]

        return list(col.aggregate(pipeline))

    @staticmethod
    def get_revisit_rate_analysis() -> Dict[str, Any]:
        """Pipeline 3: tần suất và tỷ lệ tái khám toàn viện.

        Stages: $group theo patient_id -> $facet chạy song song
        (summary, distribution bằng $bucket, top bệnh nhân) -> tính % trong $project.
        """
        col = get_records_collection()

        pipeline = [
            {
                "$group": {
                    "_id": "$patient_id",
                    "visit_count": {"$sum": 1},
                    "departments": {"$addToSet": "$department"},
                    "latest_visit": {"$max": "$visit_date"},
                }
            },
            {
                "$facet": {
                    "summary": [
                        {
                            "$group": {
                                "_id": None,
                                "total_unique_patients": {"$sum": 1},
                                "revisit_patients": {
                                    "$sum": {"$cond": [{"$gt": ["$visit_count", 1]}, 1, 0]}
                                },
                                "single_visit_patients": {
                                    "$sum": {"$cond": [{"$eq": ["$visit_count", 1]}, 1, 0]}
                                },
                                "total_visits": {"$sum": "$visit_count"},
                            }
                        }
                    ],
                    "distribution": [
                        {
                            "$bucket": {
                                "groupBy": "$visit_count",
                                "boundaries": [1, 2, 4],
                                "default": ">3",
                                "output": {"patient_count": {"$sum": 1}},
                            }
                        },
                        {
                            "$project": {
                                "_id": 0,
                                "level": {
                                    "$switch": {
                                        "branches": [
                                            {"case": {"$eq": ["$_id", 1]}, "then": "1 lần"},
                                            {"case": {"$eq": ["$_id", 2]}, "then": "2-3 lần"},
                                        ],
                                        "default": ">3 lần",
                                    }
                                },
                                "patient_count": 1,
                            }
                        },
                    ],
                    "top_patients": [
                        {"$sort": {"visit_count": -1}},
                        {"$limit": 5},
                        {
                            "$project": {
                                "_id": 0,
                                "patient_id": "$_id",
                                "visit_count": 1,
                                "departments": 1,
                                "latest_visit": 1,
                            }
                        },
                    ],
                }
            },
            {
                "$addFields": {
                    "total_unique_patients": {
                        "$ifNull": [{"$arrayElemAt": ["$summary.total_unique_patients", 0]}, 0]
                    },
                    "revisit_patients": {
                        "$ifNull": [{"$arrayElemAt": ["$summary.revisit_patients", 0]}, 0]
                    },
                    "single_visit_patients": {
                        "$ifNull": [{"$arrayElemAt": ["$summary.single_visit_patients", 0]}, 0]
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total_unique_patients": 1,
                    "revisit_patients": 1,
                    "single_visit_patients": 1,
                    "revisit_rate_percent": {
                        "$cond": [
                            {"$gt": ["$total_unique_patients", 0]},
                            {
                                "$round": [
                                    {
                                        "$multiply": [
                                            {
                                                "$divide": [
                                                    "$revisit_patients",
                                                    "$total_unique_patients",
                                                ]
                                            },
                                            100,
                                        ]
                                    },
                                    2,
                                ]
                            },
                            0.0,
                        ]
                    },
                    "distribution": 1,
                    "top_revisit_patients": "$top_patients",
                }
            },
        ]

        result = list(col.aggregate(pipeline))
        if not result:
            return {
                "total_unique_patients": 0,
                "revisit_patients": 0,
                "single_visit_patients": 0,
                "revisit_rate_percent": 0.0,
                "distribution": [],
                "top_revisit_patients": [],
            }
        return result[0]

    # Tên cũ đang được frontend Streamlit (SV3) gọi trực tiếp.
    get_revisit_statistics = get_revisit_rate_analysis
