
"""Сборка инженерного отчёта по скважине."""


def build_report(server, well_id: str, horizon_months: int = 12) -> dict:
    """Получить факт, прогноз и рабочую точку через MCP."""

    history = server.call("get_production_history", well_id=well_id, months=24)

    forecast = server.call("forecast_production", well_id=well_id, horizon_months=horizon_months)

    opened = server.call("open_well_model", well_id=well_id)

    nodal = server.call("run_nodal_analysis", session_id=opened["session_id"]    )

    if nodal["status"] != "done":
        raise ValueError("Рабочая точка не найдена")

    last_hist = history["points"][-1]
    first_fc = forecast["points"][0]
    last_fc = forecast["points"][-1]

    fit = forecast["fit"]
    op = nodal["operating_point"]

    # 6. Формируем отчёт
    report = {
        "well_id": well_id,

        "fact": {
            "date": last_hist["date"],
            "q_m3_day": last_hist["q_m3_day"],
            "unit": history["units"]["q_m3_day"],
            "source": "get_production_history"
        },

        "forecast": {
            "first": {
                "date": first_fc["date"],
                "q_m3_day": first_fc["q_m3_day"],
                "unit": forecast["units"]["q_m3_day"]
            },

            "last": {
                "date": last_fc["date"],
                "q_m3_day": last_fc["q_m3_day"],
                "unit": forecast["units"]["q_m3_day"]
            },

            "annual_decline": {
                "value": fit["annual_decline"],
                "unit": forecast["units"]["annual_decline"]
            },

            "r2": {
                "value": fit["r2"],
                "unit": "1"
            },

            "source": "forecast_production"
        },

        "operating_point": {
            "q_m3_day": op["q_m3_day"],
            "pwf_bar": op["pwf_bar"],
            "unit_q": nodal["units"]["q_m3_day"],
            "unit_pwf": nodal["units"]["pwf_bar"],
            "source": "run_nodal_analysis"
        }
    }

    return report
