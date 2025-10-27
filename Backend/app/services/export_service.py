import io
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
import json


class ExportService:
    """Servicio mejorado para exportación de análisis financieros"""
    
    def __init__(self):
        self.company_name = "Análisis Financiero"
        self.export_date = datetime.now()
    
    def create_excel_report(self, analysis_data: Dict, report_type: str = "complete") -> io.BytesIO:
        """
        Crea un reporte Excel completo con formato profesional
        
        Args:
            analysis_data: Datos del análisis financiero
            report_type: Tipo de reporte (complete, summary, indicators, analysis)
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Definir estilos
        styles = self._create_styles(workbook)
        
        # Generar diferentes tipos de reportes
        if report_type == "complete":
            self._create_complete_report(workbook, analysis_data, styles)
        elif report_type == "summary":
            self._create_summary_report(workbook, analysis_data, styles)
        elif report_type == "indicators":
            self._create_indicators_report(workbook, analysis_data, styles)
        elif report_type == "analysis":
            self._create_analysis_report(workbook, analysis_data, styles)
        elif report_type == "comparative":
            self._create_comparative_report(workbook, analysis_data, styles)
        
        workbook.close()
        output.seek(0)
        return output
    
    def _create_styles(self, workbook) -> Dict:
        """Crea los estilos para el reporte"""
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
                'font_size': 12,
                'font_color': 'white',
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#2c5282',
                'border': 1,
                'text_wrap': True
            }),
            'subheader': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'align': 'left',
                'bg_color': '#e6f2ff',
                'border': 1
            }),
            'category': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'font_color': '#2c5282',
                'bg_color': '#f7fafc',
                'border': 1,
                'left': 2
            }),
            'label': workbook.add_format({
                'align': 'left',
                'border': 1,
                'text_wrap': True
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
                'align': 'left'
            })
        }
    
    def _create_complete_report(self, workbook, data: Dict, styles: Dict):
        """Crea un reporte completo con todas las secciones"""
        # Portada
        self._add_cover_page(workbook, data, styles)
        
        # Resumen Ejecutivo
        self._add_executive_summary(workbook, data, styles)
        
        # Indicadores por categoría
        self._add_liquidity_sheet(workbook, data, styles)
        self._add_profitability_sheet(workbook, data, styles)
        self._add_debt_sheet(workbook, data, styles)
        self._add_rotation_sheet(workbook, data, styles)
        self._add_bankruptcy_sheet(workbook, data, styles)
        
        # Análisis Horizontal
        if data.get('horizontal_analysis'):
            self._add_horizontal_analysis(workbook, data, styles)
        
        # Análisis Vertical
        if data.get('vertical_analysis'):
            self._add_vertical_analysis(workbook, data, styles)
        
        # Datos Crudos
        self._add_raw_data(workbook, data, styles)
    
    def _create_summary_report(self, workbook, data: Dict, styles: Dict):
        """Crea un reporte resumen ejecutivo"""
        self._add_cover_page(workbook, data, styles)
        self._add_executive_summary(workbook, data, styles)
    
    def _create_indicators_report(self, workbook, data: Dict, styles: Dict):
        """Crea un reporte solo con indicadores"""
        self._add_liquidity_sheet(workbook, data, styles)
        self._add_profitability_sheet(workbook, data, styles)
        self._add_debt_sheet(workbook, data, styles)
        self._add_rotation_sheet(workbook, data, styles)
        self._add_bankruptcy_sheet(workbook, data, styles)
    
    def _create_analysis_report(self, workbook, data: Dict, styles: Dict):
        """Crea un reporte con análisis horizontal y vertical"""
        if data.get('horizontal_analysis'):
            self._add_horizontal_analysis(workbook, data, styles)
        if data.get('vertical_analysis'):
            self._add_vertical_analysis(workbook, data, styles)
    
    def _create_comparative_report(self, workbook, data: Dict, styles: Dict):
        """Crea un reporte comparativo entre años"""
        worksheet = workbook.add_worksheet('Comparativo')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        
        # Título
        worksheet.merge_range(row, 0, row, len(data['available_years']), 
                            'ANÁLISIS COMPARATIVO MULTIANUAL', styles['title'])
        row += 2
        
        # Encabezados
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(data['available_years'], 1):
            worksheet.write(row, col, str(year), styles['header'])
        row += 1
        
        # Indicadores por categoría
        categories = {
            'Liquidez': data['indicators'].get('liquidez', {}),
            'Rentabilidad': data['indicators'].get('rentabilidad', {}),
            'Endeudamiento': data['indicators'].get('endeudamiento', {}),
            'Rotación': data['indicators'].get('rotacion', {}),
            'Quiebra': data['indicators'].get('quiebra', {})
        }
        
        for category_name, indicators in categories.items():
            worksheet.write(row, 0, category_name, styles['category'])
            row += 1
            
            for indicator_name, values in indicators.items():
                if isinstance(values, dict):
                    label = self._get_indicator_label(indicator_name)
                    worksheet.write(row, 0, label, styles['label'])
                    
                    for col, year in enumerate(data['available_years'], 1):
                        value = values.get(str(year))
                        if value is not None:
                            format_style = self._get_value_format(indicator_name, value, styles)
                            worksheet.write(row, col, value, format_style)
                    row += 1
            row += 1
    
    def _add_cover_page(self, workbook, data: Dict, styles: Dict):
        """Agrega página de portada"""
        worksheet = workbook.add_worksheet('Portada')
        worksheet.set_column('A:A', 40)
        
        row = 5
        worksheet.merge_range(row, 0, row, 2, 'REPORTE DE ANÁLISIS FINANCIERO', styles['title'])
        
        row += 3
        info_style = workbook.add_format({'font_size': 11, 'align': 'left'})
        
        worksheet.write(row, 0, 'Empresa:', workbook.add_format({'bold': True}))
        worksheet.write(row, 1, self.company_name, info_style)
        row += 1
        
        worksheet.write(row, 0, 'Fecha de Generación:', workbook.add_format({'bold': True}))
        worksheet.write(row, 1, self.export_date.strftime('%d/%m/%Y %H:%M'), info_style)
        row += 1
        
        worksheet.write(row, 0, 'Períodos Analizados:', workbook.add_format({'bold': True}))
        worksheet.write(row, 1, ', '.join(map(str, data.get('available_years', []))), info_style)
        row += 1
        
        worksheet.write(row, 0, 'Archivo Fuente:', workbook.add_format({'bold': True}))
        worksheet.write(row, 1, data.get('filename', 'N/A'), info_style)
    
    def _add_executive_summary(self, workbook, data: Dict, styles: Dict):
        """Agrega resumen ejecutivo"""
        worksheet = workbook.add_worksheet('Resumen Ejecutivo')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 40)
        
        row = 0
        worksheet.merge_range(row, 0, row, 2, 'RESUMEN EJECUTIVO', styles['title'])
        row += 2
        
        # Obtener último año
        years = data.get('available_years', [])
        if not years:
            return
        
        latest_year = str(max(years))
        indicators = data.get('indicators', {})
        
        # Sección Liquidez
        worksheet.write(row, 0, '💧 LIQUIDEZ', styles['category'])
        row += 1
        
        liquidez = indicators.get('liquidez', {})
        razon_corriente = liquidez.get('razon_corriente', {}).get(latest_year, 0)
        clasificacion = liquidez.get('clasificacion_liquidez', {}).get(latest_year, 'N/A')
        
        worksheet.write(row, 0, 'Razón Corriente', styles['label'])
        worksheet.write(row, 1, razon_corriente, styles['number'])
        worksheet.write(row, 2, self._get_liquidity_interpretation(razon_corriente), styles['info'])
        row += 1
        
        worksheet.write(row, 0, 'Clasificación', styles['label'])
        worksheet.write(row, 1, clasificacion, styles['label'])
        row += 2
        
        # Sección Rentabilidad
        worksheet.write(row, 0, '💰 RENTABILIDAD', styles['category'])
        row += 1
        
        rentabilidad = indicators.get('rentabilidad', {})
        roe = rentabilidad.get('roe', {}).get(latest_year, 0)
        roa = rentabilidad.get('roa', {}).get(latest_year, 0)
        
        worksheet.write(row, 0, 'ROE', styles['label'])
        worksheet.write(row, 1, roe, styles['percentage'])
        worksheet.write(row, 2, self._get_roe_interpretation(roe), styles['info'])
        row += 1
        
        worksheet.write(row, 0, 'ROA', styles['label'])
        worksheet.write(row, 1, roa, styles['percentage'])
        row += 2
        
        # Sección Endeudamiento
        worksheet.write(row, 0, '📊 ENDEUDAMIENTO', styles['category'])
        row += 1
        
        endeudamiento = indicators.get('endeudamiento', {})
        endeudamiento_total = endeudamiento.get('endeudamiento_total', {}).get(latest_year, 0)
        clasificacion_riesgo = endeudamiento.get('clasificacion_riesgo', {}).get(latest_year, 'N/A')
        
        worksheet.write(row, 0, 'Endeudamiento Total', styles['label'])
        worksheet.write(row, 1, endeudamiento_total, styles['percentage'])
        worksheet.write(row, 2, self._get_debt_interpretation(endeudamiento_total), styles['info'])
        row += 1
        
        worksheet.write(row, 0, 'Clasificación de Riesgo', styles['label'])
        worksheet.write(row, 1, clasificacion_riesgo, styles['label'])
        row += 2
        
        # Sección Quiebra
        worksheet.write(row, 0, '⚠️ RIESGO DE QUIEBRA', styles['category'])
        row += 1
        
        quiebra = indicators.get('quiebra', {})
        z_score = quiebra.get('z_score', {}).get(latest_year, 0)
        clasificacion_z = quiebra.get('clasificacion_z', {}).get(latest_year, 'N/A')
        
        worksheet.write(row, 0, 'Z-Score Altman', styles['label'])
        worksheet.write(row, 1, z_score, styles['number'])
        worksheet.write(row, 2, self._get_zscore_interpretation(z_score), styles['info'])
        row += 1
        
        worksheet.write(row, 0, 'Clasificación', styles['label'])
        worksheet.write(row, 1, clasificacion_z, styles['label'])
    
    def _add_liquidity_sheet(self, workbook, data: Dict, styles: Dict):
        """Agrega hoja de indicadores de liquidez"""
        self._add_indicator_sheet(workbook, data, 'liquidez', '💧 Indicadores de Liquidez', styles)
    
    def _add_profitability_sheet(self, workbook, data: Dict, styles: Dict):
        """Agrega hoja de indicadores de rentabilidad"""
        self._add_indicator_sheet(workbook, data, 'rentabilidad', '💰 Indicadores de Rentabilidad', styles)
    
    def _add_debt_sheet(self, workbook, data: Dict, styles: Dict):
        """Agrega hoja de indicadores de endeudamiento"""
        self._add_indicator_sheet(workbook, data, 'endeudamiento', '📊 Indicadores de Endeudamiento', styles)
    
    def _add_rotation_sheet(self, workbook, data: Dict, styles: Dict):
        """Agrega hoja de indicadores de rotación"""
        self._add_indicator_sheet(workbook, data, 'rotacion', '🔄 Indicadores de Rotación', styles)
    
    def _add_bankruptcy_sheet(self, workbook, data: Dict, styles: Dict):
        """Agrega hoja de análisis de quiebra"""
        self._add_indicator_sheet(workbook, data, 'quiebra', '⚠️ Análisis de Quiebra', styles)
    
    def _add_indicator_sheet(self, workbook, data: Dict, category: str, title: str, styles: Dict):
        """Agrega una hoja de indicadores genérica"""
        worksheet = workbook.add_worksheet(title.split(' ')[-1])
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, len(data['available_years']), title, styles['title'])
        row += 2
        
        # Encabezados
        worksheet.write(row, 0, 'Indicador', styles['header'])
        for col, year in enumerate(data['available_years'], 1):
            worksheet.write(row, col, str(year), styles['header'])
        row += 1
        
        # Indicadores
        indicators = data['indicators'].get(category, {})
        for indicator_name, values in indicators.items():
            if isinstance(values, dict):
                label = self._get_indicator_label(indicator_name)
                worksheet.write(row, 0, label, styles['label'])
                
                for col, year in enumerate(data['available_years'], 1):
                    value = values.get(str(year))
                    if value is not None:
                        format_style = self._get_value_format(indicator_name, value, styles)
                        worksheet.write(row, col, value, format_style)
                row += 1
        
        # Agregar interpretaciones
        row += 1
        worksheet.write(row, 0, 'Interpretación:', styles['subheader'])
        row += 1
        worksheet.merge_range(row, 0, row + 2, len(data['available_years']), 
                            self._get_category_interpretation(category), 
                            styles['info'])
    
    def _add_horizontal_analysis(self, workbook, data: Dict, styles: Dict):
        """Agrega análisis horizontal"""
        worksheet = workbook.add_worksheet('Análisis Horizontal')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, 6, 'ANÁLISIS HORIZONTAL', styles['title'])
        row += 2
        
        horizontal = data.get('horizontal_analysis', {})
        years = data.get('available_years', [])
        
        for account_name, account_data in horizontal.items():
            worksheet.write(row, 0, self._format_account_name(account_name), styles['category'])
            row += 1
            
            # Encabezados
            worksheet.write(row, 0, 'Año', styles['header'])
            worksheet.write(row, 1, 'Valor', styles['header'])
            worksheet.write(row, 2, 'Variación Absoluta', styles['header'])
            worksheet.write(row, 3, 'Variación %', styles['header'])
            row += 1
            
            # Datos
            values = account_data.get('values', {})
            absolute_var = account_data.get('absolute_variation', {})
            percentage_var = account_data.get('percentage_variation', {})
            
            for year in years:
                year_str = str(year)
                worksheet.write(row, 0, year_str, styles['label'])
                worksheet.write(row, 1, values.get(year_str, 0), styles['currency'])
                
                if year_str in absolute_var:
                    worksheet.write(row, 2, absolute_var[year_str], styles['currency'])
                    worksheet.write(row, 3, percentage_var[year_str] / 100, styles['percentage'])
                row += 1
            
            row += 1
    
    def _add_vertical_analysis(self, workbook, data: Dict, styles: Dict):
        """Agrega análisis vertical"""
        worksheet = workbook.add_worksheet('Análisis Vertical')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, len(data['available_years']), 
                            'ANÁLISIS VERTICAL', styles['title'])
        row += 2
        
        # Encabezados
        worksheet.write(row, 0, 'Cuenta', styles['header'])
        for col, year in enumerate(data['available_years'], 1):
            worksheet.write(row, col, f'{year} (%)', styles['header'])
        row += 1
        
        # Datos
        vertical = data.get('vertical_analysis', {})
        for account_name, percentages in vertical.items():
            worksheet.write(row, 0, self._format_account_name(account_name), styles['label'])
            
            for col, year in enumerate(data['available_years'], 1):
                value = percentages.get(str(year), 0)
                worksheet.write(row, col, value / 100, styles['percentage'])
            row += 1
    
    def _add_raw_data(self, workbook, data: Dict, styles: Dict):
        """Agrega datos crudos"""
        worksheet = workbook.add_worksheet('Datos Crudos')
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:Z', 15)
        
        row = 0
        worksheet.merge_range(row, 0, row, len(data['available_years']), 
                            'DATOS FINANCIEROS CRUDOS', styles['title'])
        row += 2
        
        # Encabezados
        worksheet.write(row, 0, 'Cuenta', styles['header'])
        for col, year in enumerate(data['available_years'], 1):
            worksheet.write(row, col, str(year), styles['header'])
        row += 1
        
        # Datos
        raw_data = data.get('raw_data', {})
        for account_name, values in raw_data.items():
            worksheet.write(row, 0, self._format_account_name(account_name), styles['label'])
            
            for col, year in enumerate(data['available_years'], 1):
                value = values.get(str(year), 0)
                worksheet.write(row, col, value, styles['currency'])
            row += 1
    
    # Métodos auxiliares
    
    def _get_indicator_label(self, key: str) -> str:
        """Obtiene la etiqueta legible del indicador"""
        labels = {
            'razon_corriente': 'Razón Corriente',
            'prueba_acida': 'Prueba Ácida',
            'capital_trabajo': 'Capital de Trabajo',
            'clasificacion_liquidez': 'Clasificación',
            'roe': 'Return on Equity (ROE)',
            'roa': 'Return on Assets (ROA)',
            'margen_bruto': 'Margen Bruto',
            'margen_neto': 'Margen Neto',
            'endeudamiento_total': 'Endeudamiento Total',
            'deuda_patrimonio': 'Deuda/Patrimonio',
            'cobertura_intereses': 'Cobertura de Intereses',
            'clasificacion_riesgo': 'Clasificación de Riesgo',
            'rotacion_inventarios': 'Rotación de Inventarios',
            'rotacion_cartera': 'Rotación de Cartera',
            'rotacion_activos': 'Rotación de Activos',
            'dias_inventario': 'Días de Inventario',
            'dias_cartera': 'Días de Cartera',
            'z_score': 'Z-Score Altman',
            'clasificacion_z': 'Clasificación Z-Score',
            'probabilidad_quiebra': 'Probabilidad de Quiebra'
        }
        return labels.get(key, key.replace('_', ' ').title())
    
    def _get_value_format(self, indicator_name: str, value, styles: Dict):
        """Obtiene el formato apropiado para un valor"""
        if isinstance(value, str):
            return styles['label']
        
        # Formatos por tipo de indicador
        currency_indicators = ['capital_trabajo']
        percentage_indicators = ['roe', 'roa', 'margen_bruto', 'margen_neto', 
                                'endeudamiento_total']
        
        if indicator_name in currency_indicators:
            return styles['currency']
        elif indicator_name in percentage_indicators:
            return styles['percentage']
        else:
            # Aplicar colores según rangos
            if indicator_name == 'razon_corriente':
                if value >= 1.5:
                    return styles['good']
                elif value >= 1.0:
                    return styles['warning']
                else:
                    return styles['bad']
            elif indicator_name == 'z_score':
                if value > 2.99:
                    return styles['good']
                elif value >= 1.81:
                    return styles['warning']
                else:
                    return styles['bad']
            
            return styles['number']
    
    def _format_account_name(self, name: str) -> str:
        """Formatea nombres de cuentas"""
        return name.replace('_', ' ').title()
    
    def _get_liquidity_interpretation(self, razon: float) -> str:
        """Interpreta la razón corriente"""
        if razon >= 2.0:
            return "Excelente: Alta capacidad de pago"
        elif razon >= 1.5:
            return "Bueno: Capacidad de pago adecuada"
        elif razon >= 1.0:
            return "Aceptable: Capacidad de pago limitada"
        else:
            return "Crítico: Riesgo de liquidez"
    
    def _get_roe_interpretation(self, roe: float) -> str:
        """Interpreta el ROE"""
        if roe >= 0.15:
            return "Excelente: Alta rentabilidad sobre capital"
        elif roe >= 0.10:
            return "Bueno: Rentabilidad aceptable"
        elif roe >= 0.05:
            return "Regular: Rentabilidad baja"
        else:
            return "Crítico: Rentabilidad insuficiente"
    
    def _get_debt_interpretation(self, debt: float) -> str:
        """Interpreta el endeudamiento"""
        if debt <= 0.40:
            return "Bajo: Estructura financiera saludable"
        elif debt <= 0.60:
            return "Medio: Endeudamiento moderado"
        else:
            return "Alto: Alto riesgo financiero"
    
    def _get_zscore_interpretation(self, z_score: float) -> str:
        """Interpreta el Z-Score"""
        if z_score > 2.99:
            return "Zona Segura: Bajo riesgo de quiebra"
        elif z_score >= 1.81:
            return "Zona Gris: Riesgo moderado"
        else:
            return "Zona de Peligro: Alto riesgo de quiebra"
    
    def _get_category_interpretation(self, category: str) -> str:
        """Obtiene interpretación de la categoría"""
        interpretations = {
            'liquidez': 'Los indicadores de liquidez miden la capacidad de la empresa para cumplir con sus obligaciones a corto plazo. Una razón corriente mayor a 1.5 es considerada saludable.',
            'rentabilidad': 'Los indicadores de rentabilidad evalúan la capacidad de generar utilidades. Un ROE superior al 15% indica una excelente gestión del capital.',
            'endeudamiento': 'Los indicadores de endeudamiento miden el nivel de deuda y la capacidad de cubrirla. Un endeudamiento total inferior al 60% es recomendable.',
            'rotacion': 'Los indicadores de rotación evalúan la eficiencia operativa. Mayor rotación indica mejor gestión de recursos.',
            'quiebra': 'El Z-Score de Altman predice el riesgo de quiebra. Un valor superior a 2.99 indica zona segura.'
        }
        return interpretations.get(category, '')
    
    def export_to_csv(self, analysis_data: Dict, category: Optional[str] = None) -> io.StringIO:
        """
        Exporta datos a formato CSV
        
        Args:
            analysis_data: Datos del análisis
            category: Categoría específica a exportar (opcional)
        """
        output = io.StringIO()
        
        if category and category in analysis_data['indicators']:
            # Exportar categoría específica
            df = pd.DataFrame(analysis_data['indicators'][category])
            df = df.T  # Transponer para tener años como columnas
            df.to_csv(output)
        else:
            # Exportar todos los indicadores
            all_data = {}
            for cat_name, indicators in analysis_data['indicators'].items():
                for ind_name, values in indicators.items():
                    if isinstance(values, dict):
                        all_data[f"{cat_name}_{ind_name}"] = values
            
            df = pd.DataFrame(all_data)
            df = df.T
            df.to_csv(output)
        
        output.seek(0)
        return output
    
    def export_to_json(self, analysis_data: Dict) -> str:
        """Exporta datos a formato JSON"""
        return json.dumps(analysis_data, indent=2, ensure_ascii=False)