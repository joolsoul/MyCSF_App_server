schedule = {
    "type": "object",
    "properties": {
        "numerator": {
            "type": "object",
            "properties": {
                "monday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "tuesday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                    }
                },
                "wednesday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "thursday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "friday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "saturday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                }
            },
            "required": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday"
            ]
        },
        "denominator": {
            "type": "object",
            "properties": {
                "monday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "tuesday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "wednesday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "thursday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "friday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                },
                "saturday": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "timeFrom": {"type": "string"},
                            "timeTo": {"type": "string"},
                            "subjectName": {"type": "string"},
                            "classroom": {"type": "string"},
                            "professor": {"type": "string"},
                        },
                        "required": [
                            "timeFrom",
                            "timeTo",
                            "subjectName",
                            "classroom",
                            "professor"
                        ]
                    }
                }
            },
            "required": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday"
            ]
        }
    },
    "required": [
        "numerator",
        "denominator"
    ]
}
