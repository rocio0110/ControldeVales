@login_required
@user_passes_test(es_auditor)
def auditoria_reportes(request):

    periodo = request.GET.get("periodo", "semanal")
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    hoy = timezone.now()

    # Filtro automático por periodo
    if not fecha_inicio and not fecha_fin:
        if periodo == "semanal":
            fecha_inicio = hoy - timedelta(days=7)
        elif periodo == "quincenal":
            fecha_inicio = hoy - timedelta(days=15)
        elif periodo == "mensual":
            fecha_inicio = hoy - timedelta(days=30)
        fecha_fin = hoy

    movimientos = MovimientoSaldo.objects.all()

    if fecha_inicio and fecha_fin:
        movimientos = movimientos.filter(
            fecha__range=[fecha_inicio, fecha_fin]
        )

    total_movimientos = movimientos.count()
    total_consumo = movimientos.filter(tipo="consumo").aggregate(
        total=Sum("monto")
    )["total"] or 0

    total_recargas = movimientos.filter(tipo="recarga").aggregate(
        total=Sum("monto")
    )["total"] or 0

    # Datos para gráfica
    grafica_data = (
        movimientos.values("tipo")
        .annotate(total=Count("id"))
    )

    context = {
        "movimientos": movimientos.order_by("-fecha")[:50],
        "total_movimientos": total_movimientos,
        "total_consumo": total_consumo,
        "total_recargas": total_recargas,
        "periodo": periodo,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "grafica_labels": [g["tipo"] for g in grafica_data],
        "grafica_valores": [g["total"] for g in grafica_data],
    }

    return render(request, "auditoria/reportes.html", context)

###exportar excel

@login_required
@user_passes_test(es_auditor)
def exportar_excel_auditoria(request):

    periodo = request.GET.get("periodo", "mensual")
    hoy = timezone.now()

    if periodo == "semanal":
        fecha_inicio = hoy - timedelta(days=7)
    elif periodo == "quincenal":
        fecha_inicio = hoy - timedelta(days=15)
    else:
        fecha_inicio = hoy - timedelta(days=30)

    recargas = recargas.objects.filter(creado_en__gte=fecha_inicio)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reporte Auditoría"

    ws.append(["REPORTE DE AUDITORÍA"])
    ws.append([])
    ws.append(["Conductor", "Zona", "Preceptor", "Fecha"])

    for r in recargas:
        ws.append([
            r.conductor_1.clave,
            r.origen,
            r.creado_por.username,
            r.creado_en.strftime("%Y-%m-%d %H:%M")
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=reporte_auditoria.xlsx"

    wb.save(response)
    return response

###exportar pdf



@login_required
@user_passes_test(es_auditor)
def exportar_pdf_auditoria(request):

    periodo = request.GET.get("periodo", "mensual")
    hoy = timezone.now()

    if periodo == "semanal":
        fecha_inicio = hoy - timedelta(days=7)
    elif periodo == "quincenal":
        fecha_inicio = hoy - timedelta(days=15)
    else:
        fecha_inicio = hoy - timedelta(days=30)

    recargas = recargas.objects.filter(creado_en__gte=fecha_inicio)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=reporte_auditoria.pdf"

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Logo
    logo_path = os.path.join(settings.BASE_DIR, "static/img/logo.png")
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=2*inch, height=1*inch))
        elements.append(Spacer(1, 12))

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Reporte Oficial de Auditoría", styles["Heading1"]))
    elements.append(Spacer(1, 20))

    data = [["Conductor", "Zona", "Preceptor", "Fecha"]]

    for r in recargas:
        data.append([
            r.conductor_1.clave,
            r.origen,
            r.creado_por.username,
            r.creado_en.strftime("%Y-%m-%d %H:%M")
        ])

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    elements.append(table)
    doc.build(elements)

    return response
