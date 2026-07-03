from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.report import DashboardResponse
from app.modules.reports.service import ReportService
from app.utils.pdf_report import generate_pdf
from app.utils.excel_report import generate_excel
from app.core.permissions import require_admin, require_librarian
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    _: User = Depends(require_admin),
    service: ReportService = Depends(get_service),
):
    return await service.get_dashboard()


@router.get("/{report_type}")
async def get_report(
    report_type: str,
    start_date: str = Query(None),
    end_date: str = Query(None),
    _: User = Depends(require_admin),
    service: ReportService = Depends(get_service),
):
    valid_types = ["borrowed", "returned", "overdue", "fines", "daily", "weekly", "monthly", "yearly"]
    if report_type not in valid_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid report type. Valid: {valid_types}")
    data = await service.get_report_data(report_type, start_date, end_date)
    return data


@router.get("/export/pdf/{report_type}")
async def export_pdf(
    report_type: str,
    _: User = Depends(require_admin),
    service: ReportService = Depends(get_service),
):
    headers, rows = await service.get_export_data(report_type)
    pdf = generate_pdf(f"{report_type.title()} Report", headers, rows)
    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={report_type}_report.pdf"},
    )


@router.get("/export/excel/{report_type}")
async def export_excel(
    report_type: str,
    _: User = Depends(require_admin),
    service: ReportService = Depends(get_service),
):
    headers, rows = await service.get_export_data(report_type)
    excel = generate_excel(f"{report_type.title()} Report", headers, rows)
    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={report_type}_report.xlsx"},
    )
