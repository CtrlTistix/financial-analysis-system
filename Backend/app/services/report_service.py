import io
import xlsxwriter
from typing import Dict
from datetime import datetime


class ReportService:
    """Servicio para generación de reportes especializados"""
    
    def __init__(self):
        self.company_name = "Análisis Financiero"
        self.export_date = datetime.now()
    
    def create_liquidity_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte especializado de liquidez"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        # Portada
        self._add_report_cover(workbook, "Reporte de Liquidez", "💧", styles)
        
        # Análisis de Liquidez
        worksheet = workbook.add_worksheet('Análisis de Liquidez')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 5, '💧 ANÁLISIS DE LIQUIDEZ', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        liquidez = data['indicators'].get('liquidez', {})
        
        # Encabezados
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(years, 1):
            worksheet.write(row, col, str(year), styles['header'])
        worksheet.write(row, len(years) + 1, 'Interpretación', styles['header'])
        row += 1
        
        # Razón Corriente
        worksheet.write(row, 0, 'Razón Corriente', styles['label'])
        razon_values = liquidez.get('razon_corriente', {})
        for col, year in enumerate(years, 1):
            value = razon_values.get(str(year), 0)
            style = self._get_liquidity_style(value, styles)
            worksheet.write(row, col, value, style)
        worksheet.write(row, len(years) + 1, 'Capacidad de pagar pasivos corrientes', styles['info'])
        row += 1
        
        # Prueba Ácida
        worksheet.write(row, 0, 'Prueba Ácida', styles['label'])
        prueba_values = liquidez.get('prueba_acida', {})
        for col, year in enumerate(years, 1):
            value = prueba_values.get(str(year), 0)
            style = self._get_liquidity_style(value, styles)
            worksheet.write(row, col, value, style)
        worksheet.write(row, len(years) + 1, 'Liquidez sin considerar inventarios', styles['info'])
        row += 1
        
        # Capital de Trabajo
        worksheet.write(row, 0, 'Capital de Trabajo', styles['label'])
        capital_values = liquidez.get('capital_trabajo', {})
        for col, year in enumerate(years, 1):
            value = capital_values.get(str(year), 0)
            worksheet.write(row, col, value, styles['currency'])
        worksheet.write(row, len(years) + 1, 'Recursos para operaciones', styles['info'])
        row += 2
        
        # Interpretación y Recomendaciones
        self._add_liquidity_recommendations(worksheet, liquidez, years, styles, row)
        
        workbook.close()
        output.seek(0)
        return output
    
    def create_profitability_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte especializado de rentabilidad"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        self._add_report_cover(workbook, "Reporte de Rentabilidad", "💰", styles)
        
        worksheet = workbook.add_worksheet('Análisis Rentabilidad')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 5, '💰 ANÁLISIS DE RENTABILIDAD', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        rentabilidad = data['indicators'].get('rentabilidad', {})
        
        # Encabezados
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(years, 1):
            worksheet.write(row, col, str(year), styles['header'])
        worksheet.write(row, len(years) + 1, 'Interpretación', styles['header'])
        row += 1
        
        # ROE
        worksheet.write(row, 0, 'ROE (Return on Equity)', styles['label'])
        roe_values = rentabilidad.get('roe', {})
        for col, year in enumerate(years, 1):
            value = roe_values.get(str(year), 0)
            style = self._get_profitability_style(value, 'roe', styles)
            worksheet.write(row, col, value, styles['percentage'])
        worksheet.write(row, len(years) + 1, 'Rentabilidad sobre patrimonio', styles['info'])
        row += 1
        
        # ROA
        worksheet.write(row, 0, 'ROA (Return on Assets)', styles['label'])
        roa_values = rentabilidad.get('roa', {})
        for col, year in enumerate(years, 1):
            value = roa_values.get(str(year), 0)
            worksheet.write(row, col, value, styles['percentage'])
        worksheet.write(row, len(years) + 1, 'Rentabilidad sobre activos', styles['info'])
        row += 1
        
        # Margen Bruto
        worksheet.write(row, 0, 'Margen Bruto', styles['label'])
        margen_bruto = rentabilidad.get('margen_bruto', {})
        for col, year in enumerate(years, 1):
            value = margen_bruto.get(str(year), 0)
            worksheet.write(row, col, value, styles['percentage'])
        worksheet.write(row, len(years) + 1, 'Utilidad bruta / Ventas', styles['info'])
        row += 1
        
        # Margen Neto
        worksheet.write(row, 0, 'Margen Neto', styles['label'])
        margen_neto = rentabilidad.get('margen_neto', {})
        for col, year in enumerate(years, 1):
            value = margen_neto.get(str(year), 0)
            worksheet.write(row, col, value, styles['percentage'])
        worksheet.write(row, len(years) + 1, 'Utilidad neta / Ventas', styles['info'])
        row += 2
        
        # Recomendaciones
        self._add_profitability_recommendations(worksheet, rentabilidad, years, styles, row)
        
        workbook.close()
        output.seek(0)
        return output
    
    def create_debt_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte de endeudamiento"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        self._add_report_cover(workbook, "Reporte de Endeudamiento", "📉", styles)
        
        worksheet = workbook.add_worksheet('Análisis Endeudamiento')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 5, '📉 ANÁLISIS DE ENDEUDAMIENTO', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        endeudamiento = data['indicators'].get('endeudamiento', {})
        
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(years, 1):
            worksheet.write(row, col, str(year), styles['header'])
        worksheet.write(row, len(years) + 1, 'Interpretación', styles['header'])
        row += 1
        
        # Endeudamiento Total
        worksheet.write(row, 0, 'Endeudamiento Total', styles['label'])
        endeud_total = endeudamiento.get('endeudamiento_total', {})
        for col, year in enumerate(years, 1):
            value = endeud_total.get(str(year), 0)
            style = self._get_debt_style(value, styles)
            worksheet.write(row, col, value, styles['percentage'])
        worksheet.write(row, len(years) + 1, 'Pasivos / Activos totales', styles['info'])
        row += 1
        
        # Deuda/Patrimonio
        worksheet.write(row, 0, 'Deuda / Patrimonio', styles['label'])
        deuda_pat = endeudamiento.get('deuda_patrimonio', {})
        for col, year in enumerate(years, 1):
            value = deuda_pat.get(str(year), 0)
            worksheet.write(row, col, value, styles['number'])
        worksheet.write(row, len(years) + 1, 'Apalancamiento financiero', styles['info'])
        row += 1
        
        # Cobertura de Intereses
        worksheet.write(row, 0, 'Cobertura de Intereses', styles['label'])
        cobertura = endeudamiento.get('cobertura_intereses', {})
        for col, year in enumerate(years, 1):
            value = cobertura.get(str(year), 0)
            worksheet.write(row, col, value, styles['number'])
        worksheet.write(row, len(years) + 1, 'Capacidad de pagar intereses', styles['info'])
        row += 2
        
        self._add_debt_recommendations(worksheet, endeudamiento, years, styles, row)
        
        workbook.close()
        output.seek(0)
        return output
    
    def create_efficiency_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte de eficiencia operativa"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        self._add_report_cover(workbook, "Reporte de Eficiencia Operativa", "🔄", styles)
        
        worksheet = workbook.add_worksheet('Eficiencia Operativa')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 5, '🔄 ANÁLISIS DE EFICIENCIA', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        rotacion = data['indicators'].get('rotacion', {})
        
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(years, 1):
            worksheet.write(row, col, str(year), styles['header'])
        worksheet.write(row, len(years) + 1, 'Interpretación', styles['header'])
        row += 1
        
        # Indicadores de rotación
        indicators = [
            ('rotacion_inventarios', 'Rotación de Inventarios', 'Veces que se vende el inventario'),
            ('dias_inventario', 'Días de Inventario', 'Tiempo promedio en almacén'),
            ('rotacion_cartera', 'Rotación de Cartera', 'Eficiencia en cobro'),
            ('dias_cartera', 'Días de Cartera', 'Tiempo promedio de cobro'),
            ('rotacion_activos', 'Rotación de Activos', 'Eficiencia uso de activos')
        ]
        
        for indicator_key, indicator_name, interpretation in indicators:
            worksheet.write(row, 0, indicator_name, styles['label'])
            values = rotacion.get(indicator_key, {})
            for col, year in enumerate(years, 1):
                value = values.get(str(year), 0)
                worksheet.write(row, col, value, styles['number'])
            worksheet.write(row, len(years) + 1, interpretation, styles['info'])
            row += 1
        
        row += 1
        self._add_efficiency_recommendations(worksheet, rotacion, years, styles, row)
        
        workbook.close()
        output.seek(0)
        return output
    
    def create_risk_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte de análisis de riesgo"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        self._add_report_cover(workbook, "Reporte de Análisis de Riesgo", "⚠️", styles)
        
        worksheet = workbook.add_worksheet('Análisis de Riesgo')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 5, '⚠️ ANÁLISIS DE RIESGO FINANCIERO', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        quiebra = data['indicators'].get('quiebra', {})
        
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(years, 1):
            worksheet.write(row, col, str(year), styles['header'])
        worksheet.write(row, len(years) + 1, 'Estado', styles['header'])
        row += 1
        
        # Z-Score
        worksheet.write(row, 0, 'Z-Score Altman', styles['label'])
        z_score_values = quiebra.get('z_score', {})
        for col, year in enumerate(years, 1):
            value = z_score_values.get(str(year), 0)
            style = self._get_zscore_style(value, styles)
            worksheet.write(row, col, value, style)
        latest_year = str(max(years))
        latest_z = z_score_values.get(latest_year, 0)
        worksheet.write(row, len(years) + 1, self._interpret_zscore(latest_z), styles['info'])
        row += 1
        
        # Clasificación
        worksheet.write(row, 0, 'Clasificación', styles['label'])
        clasificacion = quiebra.get('clasificacion_z', {})
        for col, year in enumerate(years, 1):
            value = clasificacion.get(str(year), 'N/A')
            worksheet.write(row, col, value, styles['label'])
        row += 1
        
        # Probabilidad de Quiebra
        worksheet.write(row, 0, 'Probabilidad Quiebra', styles['label'])
        probabilidad = quiebra.get('probabilidad_quiebra', {})
        for col, year in enumerate(years, 1):
            value = probabilidad.get(str(year), 'N/A')
            worksheet.write(row, col, value, styles['label'])
        row += 2
        
        self._add_risk_recommendations(worksheet, quiebra, years, styles, row)
        
        workbook.close()
        output.seek(0)
        return output
    
    def create_executive_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte ejecutivo resumido"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        self._add_report_cover(workbook, "Reporte Ejecutivo", "📋", styles)
        
        # Dashboard Ejecutivo
        worksheet = workbook.add_worksheet('Dashboard Ejecutivo')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:C', 20)
        
        row = 0
        worksheet.merge_range(row, 0, row, 2, '📋 DASHBOARD EJECUTIVO', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        latest_year = str(max(years))
        
        # KPIs Principales
        worksheet.write(row, 0, 'INDICADORES CLAVE (KPIs)', styles['category'])
        row += 1
        
        kpis = [
            ('Liquidez', data['indicators']['liquidez']['razon_corriente'].get(latest_year, 0), 'number'),
            ('ROE', data['indicators']['rentabilidad']['roe'].get(latest_year, 0), 'percentage'),
            ('Endeudamiento', data['indicators']['endeudamiento']['endeudamiento_total'].get(latest_year, 0), 'percentage'),
            ('Z-Score', data['indicators']['quiebra']['z_score'].get(latest_year, 0), 'number')
        ]
        
        for kpi_name, value, format_type in kpis:
            worksheet.write(row, 0, kpi_name, styles['label'])
            if format_type == 'percentage':
                worksheet.write(row, 1, value, styles['percentage'])
            else:
                worksheet.write(row, 1, value, styles['number'])
            worksheet.write(row, 2, self._get_kpi_status(kpi_name, value), styles['info'])
            row += 1
        
        row += 1
        self._add_executive_summary(worksheet, data, years, styles, row)
        
        workbook.close()
        output.seek(0)
        return output
    
    def create_complete_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte completo con todas las secciones"""
        # Usar el ExportService para el reporte completo
        from app.services.export_service import ExportService
        export_service = ExportService()
        return export_service.create_excel_report(data, "complete")
    
    def create_sector_comparison_report(self, data: Dict) -> io.BytesIO:
        """Genera reporte comparativo sectorial con benchmarks"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        styles = self._create_styles(workbook)
        
        self._add_report_cover(workbook, "Comparativo Sectorial", "📈", styles)
        
        worksheet = workbook.add_worksheet('Benchmarking')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:D', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 3, '📈 COMPARATIVO SECTORIAL', styles['title'])
        row += 2
        
        years = data.get('available_years', [])
        latest_year = str(max(years))
        
        # Benchmarks sectoriales (valores promedio de industria)
        sector_benchmarks = {
            'liquidez': {
                'razon_corriente': 1.5,
                'nombre': 'Razón Corriente'
            },
            'rentabilidad': {
                'roe': 0.12,
                'nombre': 'ROE'
            },
            'endeudamiento': {
                'endeudamiento_total': 0.50,
                'nombre': 'Endeudamiento'
            }
        }
        
        worksheet.write(row, 0, 'Indicador', styles['header'])
        worksheet.write(row, 1, 'Su Empresa', styles['header'])
        worksheet.write(row, 2, 'Promedio Sector', styles['header'])
        worksheet.write(row, 3, 'Posición', styles['header'])
        row += 1
        
        # Comparaciones
        razon = data['indicators']['liquidez']['razon_corriente'].get(latest_year, 0)
        worksheet.write(row, 0, 'Razón Corriente', styles['label'])
        worksheet.write(row, 1, razon, styles['number'])
        worksheet.write(row, 2, 1.5, styles['number'])
        worksheet.write(row, 3, 'Superior' if razon > 1.5 else 'Inferior', styles['info'])
        row += 1
        
        roe = data['indicators']['rentabilidad']['roe'].get(latest_year, 0)
        worksheet.write(row, 0, 'ROE', styles['label'])
        worksheet.write(row, 1, roe, styles['percentage'])
        worksheet.write(row, 2, 0.12, styles['percentage'])
        worksheet.write(row, 3, 'Superior' if roe > 0.12 else 'Inferior', styles['info'])
        row += 1
        
        endeud = data['indicators']['endeudamiento']['endeudamiento_total'].get(latest_year, 0)
        worksheet.write(row, 0, 'Endeudamiento', styles['label'])
        worksheet.write(row, 1, endeud, styles['percentage'])
        worksheet.write(row, 2, 0.50, styles['percentage'])
        worksheet.write(row, 3, 'Mayor' if endeud > 0.50 else 'Menor', styles['info'])
        row += 2
        
        # Conclusiones
        worksheet.write(row, 0, 'CONCLUSIONES', styles['category'])
        row += 1
        worksheet.merge_range(row, 0, row + 3, 3, 
            'Este análisis compara los indicadores de su empresa con los promedios del sector. '
            'Los valores superiores en liquidez y rentabilidad indican mejor desempeño, mientras que '
            'un endeudamiento menor al promedio sugiere una estructura financiera más conservadora.',
            styles['info'])
        
        workbook.close()
        output.seek(0)
        return output
    
    # Métodos auxiliares
    
    def _create_styles(self, workbook) -> Dict:
        """Crea estilos para el reporte"""
        return {
            'title': workbook.add_format({
                'bold': True,
                'font_size': 16,
                'font_color': '#1a365d',
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#e6f2ff',
                'border': 1
            }),
            'header': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2c5282',
                'border': 1
            }),
            'category': workbook.add_format({
                'bold': True,
                'font_size': 12,
                'font_color': '#2c5282',
                'bg_color': '#f7fafc',
                'border': 1
            }),
            'label': workbook.add_format({
                'align': 'left',
                'border': 1
            }),
            'number': workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right',
                'border': 1
            }),
            'currency': workbook.add_format({
                'num_format': '$#,##0',
                'align': 'right',
                'border': 1
            }),
            'percentage': workbook.add_format({
                'num_format': '0.00%',
                'align': 'right',
                'border': 1
            }),
            'good': workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right',
                'bg_color': '#c6f6d5',
                'border': 1
            }),
            'warning': workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right',
                'bg_color': '#fef5e7',
                'border': 1
            }),
            'bad': workbook.add_format({
                'num_format': '#,##0.00',
                'align': 'right',
                'bg_color': '#fed7d7',
                'border': 1
            }),
            'info': workbook.add_format({
                'italic': True,
                'font_size': 9,
                'font_color': '#718096',
                'align': 'left',
                'text_wrap': True
            })
        }
    
    def _add_report_cover(self, workbook, title: str, icon: str, styles: Dict):
        """Agrega portada al reporte"""
        worksheet = workbook.add_worksheet('Portada')
        worksheet.set_column('A:A', 50)
        
        row = 5
        worksheet.merge_range(row, 0, row, 2, f'{icon} {title}', styles['title'])
        row += 3
        
        info_style = workbook.add_format({'font_size': 11})
        worksheet.write(row, 0, 'Fecha:', workbook.add_format({'bold': True}))
        worksheet.write(row, 1, self.export_date.strftime('%d/%m/%Y'), info_style)
        row += 1
        
        worksheet.write(row, 0, 'Generado por:', workbook.add_format({'bold': True}))
        worksheet.write(row, 1, 'Sistema de Análisis Financiero', info_style)
    
    def _get_liquidity_style(self, value: float, styles: Dict):
        """Obtiene estilo según el valor de liquidez"""
        if value >= 1.5:
            return styles['good']
        elif value >= 1.0:
            return styles['warning']
        else:
            return styles['bad']
    
    def _get_profitability_style(self, value: float, indicator_type: str, styles: Dict):
        """Obtiene estilo según rentabilidad"""
        if indicator_type == 'roe':
            if value >= 0.15:
                return styles['good']
            elif value >= 0.10:
                return styles['warning']
        return styles['number']
    
    def _get_debt_style(self, value: float, styles: Dict):
        """Obtiene estilo según endeudamiento"""
        if value <= 0.40:
            return styles['good']
        elif value <= 0.60:
            return styles['warning']
        else:
            return styles['bad']
    
    def _get_zscore_style(self, value: float, styles: Dict):
        """Obtiene estilo según Z-Score"""
        if value > 2.99:
            return styles['good']
        elif value >= 1.81:
            return styles['warning']
        else:
            return styles['bad']
    
    def _interpret_zscore(self, z_score: float) -> str:
        """Interpreta el Z-Score"""
        if z_score > 2.99:
            return "Zona Segura - Bajo riesgo"
        elif z_score >= 1.81:
            return "Zona Gris - Riesgo moderado"
        else:
            return "Zona Peligro - Alto riesgo"
    
    def _get_kpi_status(self, kpi_name: str, value: float) -> str:
        """Obtiene estado del KPI"""
        if kpi_name == 'Liquidez':
            return "Saludable" if value >= 1.5 else "Atención"
        elif kpi_name == 'ROE':
            return "Excelente" if value >= 0.15 else "Mejorable"
        elif kpi_name == 'Endeudamiento':
            return "Controlado" if value <= 0.60 else "Alto"
        elif kpi_name == 'Z-Score':
            return "Seguro" if value > 2.99 else "Riesgo"
        return "N/A"
    
    # Métodos de recomendaciones (simplificados)
    
    def _add_liquidity_recommendations(self, worksheet, data, years, styles, row):
        """Agrega recomendaciones de liquidez"""
        worksheet.write(row, 0, 'RECOMENDACIONES', styles['category'])
        row += 1
        recommendations = [
            "• Mantener una razón corriente superior a 1.5 para asegurar liquidez",
            "• Monitorear el capital de trabajo mensualmente",
            "• Reducir inventarios obsoletos para mejorar prueba ácida"
        ]
        for rec in recommendations:
            worksheet.write(row, 0, rec, styles['info'])
            row += 1
    
    def _add_profitability_recommendations(self, worksheet, data, years, styles, row):
        """Agrega recomendaciones de rentabilidad"""
        worksheet.write(row, 0, 'RECOMENDACIONES', styles['category'])
        row += 1
        recommendations = [
            "• Buscar mejorar márgenes mediante control de costos",
            "• Optimizar uso de activos para aumentar ROA",
            "• Evaluar estrategias de pricing para mejorar rentabilidad"
        ]
        for rec in recommendations:
            worksheet.write(row, 0, rec, styles['info'])
            row += 1
    
    def _add_debt_recommendations(self, worksheet, data, years, styles, row):
        """Agrega recomendaciones de endeudamiento"""
        worksheet.write(row, 0, 'RECOMENDACIONES', styles['category'])
        row += 1
        recommendations = [
            "• Mantener endeudamiento total bajo 60%",
            "• Asegurar cobertura de intereses superior a 3x",
            "• Evaluar reestructuración de deuda si es necesario"
        ]
        for rec in recommendations:
            worksheet.write(row, 0, rec, styles['info'])
            row += 1
    
    def _add_efficiency_recommendations(self, worksheet, data, years, styles, row):
        """Agrega recomendaciones de eficiencia"""
        worksheet.write(row, 0, 'RECOMENDACIONES', styles['category'])
        row += 1
        recommendations = [
            "• Reducir días de inventario mediante mejor gestión",
            "• Mejorar políticas de cobro para reducir días de cartera",
            "• Optimizar uso de activos productivos"
        ]
        for rec in recommendations:
            worksheet.write(row, 0, rec, styles['info'])
            row += 1
    
    def _add_risk_recommendations(self, worksheet, data, years, styles, row):
        """Agrega recomendaciones de riesgo"""
        worksheet.write(row, 0, 'ACCIONES RECOMENDADAS', styles['category'])
        row += 1
        recommendations = [
            "• Monitorear Z-Score trimestralmente",
            "• Implementar plan de contingencia si Z-Score < 2.0",
            "• Fortalecer liquidez y rentabilidad como prioridad"
        ]
        for rec in recommendations:
            worksheet.write(row, 0, rec, styles['info'])
            row += 1
    
    def _add_executive_summary(self, worksheet, data, years, styles, row):
        """Agrega resumen ejecutivo"""
        worksheet.write(row, 0, 'RESUMEN EJECUTIVO', styles['category'])
        row += 1
        summary = [
            "Estado General: Revisar indicadores de liquidez y rentabilidad",
            "Áreas de Fortaleza: Identificar indicadores en rangos saludables",
            "Áreas de Mejora: Priorizar indicadores en zona de atención",
            "Próximos Pasos: Implementar plan de acción basado en análisis"
        ]
        for item in summary:
            worksheet.merge_range(row, 0, row, 2, item, styles['info'])
            row += 1