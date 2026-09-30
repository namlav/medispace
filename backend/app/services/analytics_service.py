from typing import List, Dict, Any
from datetime import datetime
from backend.app.core.database import get_records_collection, get_patients_collection

class AnalyticsService:
    @staticmethod
    def get_department_stats(year: int = None) -> List[Dict[str, Any]]:
        """
        Aggregation Pipeline 1: Thống kê số lượng ca khám theo chuyên khoa.
        Stages: $match (lọc theo năm nếu có) -> $group (nhóm theo chuyên khoa) -> $sort
        """
        col = get_records_collection()
        pipeline = []
        
        if year:
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            pipeline.append({
                "$match": {
                    "visit_date": {"$gte": start_date, "$lt": end_date}
                }
            })
            
        pipeline.extend([
            {
                "$group": {
                    "_id": "$department",
                    "total_visits": {"$sum": 1},
                    "follow_up_count": {
                        "$sum": {"$cond": [{"$eq": ["$follow_up_required", True]}, 1, 0]}
                    },
                    "unique_doctors": {"$addToSet": "$doctor_name"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "department": "$_id",
                    "total_visits": 1,
                    "follow_up_count": 1,
                    "doctor_count": {"$size": "$unique_doctors"}
                }
            },
            {"$sort": {"total_visits": -1}}
        ])
        
        return list(col.aggregate(pipeline))

    @staticmethod
    def get_age_group_distribution() -> List[Dict[str, Any]]:
        """
        Aggregation Pipeline 2: Thống kê ca bệnh theo nhóm tuổi của bệnh nhân.
        Stages: $addFields -> $lookup -> $unwind -> tính tuổi -> $bucket/$switch -> $group
        """
        col = get_records_collection()
        pipeline = [
            # Chuyển patient_id chuỗi sang ObjectId để join với patients
            {
                "$addFields": {
                    "patient_obj_id": {
                        "$convert": {
                            "input": "$patient_id",
                            "to": "objectId",
                            "onError": None,
                            "onNull": None
                        }
                    }
                }
            },
            {
                "$lookup": {
                    "from": "patients",
                    "localField": "patient_obj_id",
                    "foreignField": "_id",
                    "as": "patient_info"
                }
            },
            {"$unwind": "$patient_info"},
            # Phân loại nhóm tuổi dựa trên năm sinh
            {
                "$addFields": {
                    "birth_year": {
                        "$toInt": {"$substrBytes": ["$patient_info.dob", 0, 4]}
                    }
                }
            },
            {
                "$addFields": {
                    "approx_age": {"$subtract": [datetime.utcnow().year, "$birth_year"]}
                }
            },
            {
                "$addFields": {
                    "age_group": {
                        "$switch": {
                            "branches": [
                                {"case": {"$lt": ["$approx_age", 18]}, "then": "Dưới 18 tuổi (Nhi)"},
                                {"case": {"$and": [{"$gte": ["$approx_age", 18]}, {"$lte": ["$approx_age", 40]}]}, "then": "18 - 40 tuổi (Thanh niên)"},
                                {"case": {"$and": [{"$gte": ["$approx_age", 41]}, {"$lte": ["$approx_age", 60]}]}, "then": "41 - 60 tuổi (Trung niên)"}
                            ],
                            "default": "Trên 60 tuổi (Cao tuổi)"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "age_group": "$age_group",
                        "department": "$department"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "age_group": "$_id.age_group",
                    "department": "$_id.department",
                    "count": 1
                }
            },
            {"$sort": {"age_group": 1, "count": -1}}
        ]
        
        return list(col.aggregate(pipeline))

    @staticmethod
    def get_revisit_statistics() -> Dict[str, Any]:
        """
        Aggregation Pipeline 3: Thống kê tần suất và tỷ lệ tái khám của bệnh nhân.
        Stages: $group theo patient_id tính số lần khám -> $facet để tính tỷ lệ tổng hợp và top bệnh nhân
        """
        col = get_records_collection()
        pipeline = [
            {
                "$group": {
                    "_id": "$patient_id",
                    "visit_count": {"$sum": 1},
                    "departments": {"$addToSet": "$department"},
                    "latest_visit": {"$max": "$visit_date"}
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
                                "total_visits": {"$sum": "$visit_count"}
                            }
                        }
                    ],
                    "distribution": [
                        {
                            "$bucket": {
                                "groupBy": "$visit_count",
                                "boundaries": [1, 2, 4, 6, 100],
                                "default": "Khác",
                                "output": {
                                    "patient_count": {"$sum": 1}
                                }
                            }
                        }
                    ],
                    "top_revisit_patients": [
                        {"$sort": {"visit_count": -1}},
                        {"$limit": 5}
                    ]
                }
            }
        ]
        
        result = list(col.aggregate(pipeline))
        if not result or not result[0]["summary"]:
            return {
                "total_unique_patients": 0,
                "revisit_patients": 0,
                "single_visit_patients": 0,
                "revisit_rate_percent": 0.0,
                "distribution": [],
                "top_patients": []
            }
            
        summary = result[0]["summary"][0]
        total_pts = summary.get("total_unique_patients", 0)
        revisit_pts = summary.get("revisit_patients", 0)
        revisit_rate = round((revisit_pts / total_pts * 100), 2) if total_pts > 0 else 0.0
        
        return {
            "total_unique_patients": total_pts,
            "revisit_patients": revisit_pts,
            "single_visit_patients": summary.get("single_visit_patients", 0),
            "revisit_rate_percent": revisit_rate,
            "distribution": result[0].get("distribution", []),
            "top_revisit_patients": result[0].get("top_revisit_patients", [])
        }
