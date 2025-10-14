import pandas as pd
from typing import Dict, List
import numpy as np
import re

class AnalysisService:
    def analyze_financial_data(self, df: pd.DataFrame) -> Dict:
        """Analiza datos financieros con detección mejorada"""
        
        print(f"\n{'='*60}")
        print(f"🔍 Iniciando análisis con {len(df.columns)} columnas y {len(df)} filas")
        print(f"{'='*60}\n")
        
        df_clean = self._clean_dataframe(df)
        analysis_result = self._analyze_data_structure(df_clean)
        
        if not analysis_result['success']:
            print(f"❌ Error en análisis: {analysis_result.get('error', 'Desconocido')}")
            return self._get_empty_analysis()
        
        print(f"✅ Estructura detectada exitosamente")
        return analysis_result['data']
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y prepara el DataFrame"""
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        df = df.reset_index(drop=True)
        return df
    
    def _find_year_row(self, df: pd.DataFrame) -> int:
        """Encuentra la fila que contiene los años"""
        print("\n🔎 BUSCANDO FILA DE AÑOS...")
        
        for idx, row in df.iterrows():
            year_count = 0
            years_found = []
            
            for col_idx, cell in enumerate(row):
                cell_str = str(cell).strip()
                
                if cell_str.isdigit() and 2000 <= int(cell_str) <= 2030:
                    year_count += 1
                    years_found.append(cell_str)
                    continue
                
                year_matches = re.findall(r'\b(20[0-2][0-9])\b', cell_str)
                if year_matches:
                    year_count += len(year_matches)
                    years_found.extend(year_matches)
                    continue
                
                date_patterns = [
                    r'(\d{4})-\d{2}-\d{2}',
                    r'\d{2}/\d{2}/(\d{4})',
                    r'\d{2}-\d{2}-(\d{4})',
                ]
                for pattern in date_patterns:
                    matches = re.findall(pattern, cell_str)
                    if matches:
                        year_count += len(matches)
                        years_found.extend(matches)
                        break
            
            if year_count >= 2:
                print(f"✅ Fila {idx} contiene {year_count} años: {years_found}")
                return idx
        
        print("❌ No se encontró ninguna fila con años")
        return None
    
    def _extract_years_from_row(self, df: pd.DataFrame, row_idx: int) -> List[int]:
        """Extrae años de una fila específica"""
        years = []
        row = df.iloc[row_idx]
        
        print(f"\n📅 EXTRAYENDO AÑOS DE FILA {row_idx}...")
        
        for col_idx, cell in enumerate(row):
            cell_str = str(cell).strip()
            
            if cell_str.isdigit() and 2000 <= int(cell_str) <= 2030:
                year = int(cell_str)
                if year not in years:
                    years.append(year)
                    print(f"   Columna {col_idx}: Año {year}")
                continue
            
            year_matches = re.findall(r'\b(20[0-2][0-9])\b', cell_str)
            for match in year_matches:
                year = int(match)
                if year not in years:
                    years.append(year)
                    print(f"   Columna {col_idx}: Año {year}")
        
        years = sorted(years)
        print(f"✅ Años extraídos: {years}")
        return years
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict:
        """Analiza la estructura del DataFrame y extrae datos"""
        try:
            year_row_idx = self._find_year_row(df)
            if year_row_idx is None:
                return {'success': False, 'error': 'No se encontraron años en el archivo'}
            
            years = self._extract_years_from_row(df, year_row_idx)
            if not years:
                return {'success': False, 'error': 'No se pudieron extraer años válidos'}
            
            print(f"\n📊 AÑOS DETECTADOS: {years}")
            
            financial_values = self._extract_financial_values(df, years, year_row_idx)
            
            indicators_by_year = {}
            for year in years:
                indicators_by_year[year] = self._calculate_all_indicators(financial_values, year)
            
            # Calcular análisis horizontal y vertical
            horizontal_analysis = self._calculate_horizontal_analysis(financial_values, years)
            vertical_analysis = self._calculate_vertical_analysis(financial_values, years)
            
            return {
                'success': True,
                'data': self._structure_for_frontend(
                    indicators_by_year, 
                    years, 
                    financial_values,
                    horizontal_analysis,
                    vertical_analysis
                )
            }
            
        except Exception as e:
            print(f"\n❌ ERROR en análisis de estructura: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _calculate_horizontal_analysis(self, financial_values: Dict, years: List[int]) -> Dict:
        """Calcula análisis horizontal (variaciones entre períodos)"""
        print("\n📈 CALCULANDO ANÁLISIS HORIZONTAL...")
        
        horizontal = {}
        
        # Cuentas principales para análisis
        main_accounts = [
            'activo_corriente', 'activo_total', 'pasivo_corriente', 
            'pasivo_total', 'patrimonio', 'ingresos', 'ventas',
            'costo_ventas', 'utilidad_bruta', 'utilidad_neta'
        ]
        
        for account in main_accounts:
            if account not in financial_values:
                continue
            
            horizontal[account] = {
                'values': {},
                'absolute_variation': {},
                'percentage_variation': {}
            }
            
            for i, year in enumerate(years):
                current_value = financial_values[account].get(year, 0)
                horizontal[account]['values'][str(year)] = current_value
                
                if i > 0:
                    previous_year = years[i-1]
                    previous_value = financial_values[account].get(previous_year, 0)
                    
                    # Variación absoluta
                    absolute_var = current_value - previous_value
                    horizontal[account]['absolute_variation'][str(year)] = absolute_var
                    
                    # Variación porcentual
                    if previous_value != 0:
                        percentage_var = ((current_value - previous_value) / previous_value) * 100
                    else:
                        percentage_var = 0
                    horizontal[account]['percentage_variation'][str(year)] = percentage_var
                    
                    print(f"   {account} {year}: ${current_value:,.0f} ({percentage_var:+.1f}%)")
        
        return horizontal
    
    def _calculate_vertical_analysis(self, financial_values: Dict, years: List[int]) -> Dict:
        """Calcula análisis vertical (estructura porcentual)"""
        print("\n📊 CALCULANDO ANÁLISIS VERTICAL...")
        
        vertical = {}
        
        # Análisis vertical del Balance (sobre Activo Total)
        balance_accounts = [
            'activo_corriente', 'activo_total', 'pasivo_corriente',
            'pasivo_total', 'patrimonio', 'inventario', 'cuentas_por_cobrar'
        ]
        
        for account in balance_accounts:
            if account not in financial_values:
                continue
            
            vertical[account] = {}
            
            for year in years:
                account_value = financial_values[account].get(year, 0)
                activo_total = financial_values['activo_total'].get(year, 0)
                
                if activo_total != 0 and account != 'activo_total':
                    percentage = (account_value / activo_total) * 100
                elif account == 'activo_total':
                    percentage = 100.0
                else:
                    percentage = 0.0
                
                vertical[account][str(year)] = percentage
                print(f"   {account} {year}: {percentage:.1f}% del Activo Total")
        
        # Análisis vertical del Estado de Resultados (sobre Ingresos)
        income_accounts = [
            'ingresos', 'ventas', 'costo_ventas', 'utilidad_bruta', 
            'utilidad_neta', 'gastos_intereses'
        ]
        
        for account in income_accounts:
            if account not in financial_values:
                continue
            
            if account not in vertical:
                vertical[account] = {}
            
            for year in years:
                account_value = financial_values[account].get(year, 0)
                ingresos = financial_values['ingresos'].get(year, 0) or financial_values['ventas'].get(year, 0)
                
                if ingresos != 0 and account not in ['ingresos', 'ventas']:
                    percentage = (account_value / ingresos) * 100
                elif account in ['ingresos', 'ventas']:
                    percentage = 100.0
                else:
                    percentage = 0.0
                
                vertical[account][str(year)] = percentage
        
        return vertical
    
    def _extract_financial_values(self, df: pd.DataFrame, years: List[int], year_row_idx: int) -> Dict:
        """Extrae valores financieros basado en la estructura detectada"""
        financial_data = {
            'activo_corriente': {},
            'pasivo_corriente': {},
            'inventario': {},
            'utilidad_neta': {},
            'patrimonio': {},
            'activo_total': {},
            'pasivo_total': {},
            'utilidad_bruta': {},
            'ingresos': {},
            'ventas': {},
            'costo_ventas': {},
            'cuentas_por_cobrar': {},
            'gastos_intereses': {},
            'utilidad_antes_impuestos': {},
            'capital_trabajo': {}
        }
        
        search_terms = {
            'activo_corriente': ['activo corriente', 'activos corrientes', 'activo circulante'],
            'pasivo_corriente': ['pasivo corriente', 'pasivos corrientes', 'pasivo circulante'],
            'inventario': ['inventario', 'inventarios', 'existencias'],
            'utilidad_neta': ['utilidad neta', 'utilidad del ejercicio', 'resultado neto', 'ganancia neta'],
            'patrimonio': ['patrimonio', 'capital', 'patrimonio neto', 'fondos propios'],
            'activo_total': ['activo total', 'total activo', 'total de activos', 'total activos'],
            'pasivo_total': ['pasivo total', 'total pasivo', 'total de pasivos', 'total pasivos'],
            'utilidad_bruta': ['utilidad bruta', 'beneficio bruto', 'margen bruto'],
            'ingresos': ['ingresos', 'ingresos operacionales', 'ingresos operativos'],
            'ventas': ['ventas', 'ventas netas', 'ingreso por ventas'],
            'costo_ventas': ['costo de ventas', 'costo ventas', 'costo de los bienes vendidos'],
            'cuentas_por_cobrar': ['cuentas por cobrar', 'clientes', 'deudores comerciales', 'deudores'],
            'gastos_intereses': ['gastos financieros', 'intereses', 'gastos por intereses', 'costo financiero'],
            'utilidad_antes_impuestos': ['utilidad antes de impuestos', 'ebt', 'beneficio antes de impuestos'],
            'capital_trabajo': ['capital de trabajo', 'working capital', 'capital operativo']
        }
        
        for year in years:
            year_col_idx = self._find_year_column(df, year, year_row_idx)
            if year_col_idx is not None:
                for concept, terms in search_terms.items():
                    value = self._find_concept_value(df, terms, year_col_idx, year_row_idx)
                    financial_data[concept][year] = value
        
        return financial_data
    
    def _find_year_column(self, df: pd.DataFrame, year: int, year_row_idx: int) -> int:
        """Encuentra la columna para un año específico"""
        row = df.iloc[year_row_idx]
        for col_idx, cell in enumerate(row):
            cell_str = str(cell)
            if str(year) in cell_str:
                return col_idx
        return None
    
    def _find_concept_value(self, df: pd.DataFrame, search_terms: List[str], year_col: int, year_row: int) -> float:
        """Encuentra el valor de un concepto financiero"""
        for idx, row in df.iterrows():
            if idx <= year_row:
                continue
            
            for cell in row.iloc[:3]:
                cell_str = str(cell).lower().strip()
                
                if any(term in cell_str for term in search_terms):
                    value = row.iloc[year_col]
                    try:
                        if isinstance(value, str):
                            value_clean = value.replace('$', '').replace(',', '').replace(' ', '').strip()
                            if '(' in value_clean and ')' in value_clean:
                                value_clean = '-' + value_clean.replace('(', '').replace(')', '')
                            if value_clean:
                                return float(value_clean)
                            else:
                                return 0.0
                        return float(value) if pd.notna(value) else 0.0
                    except (ValueError, TypeError):
                        return 0.0
        return 0.0
    
    def _safe_float(self, value):
        """Convierte valores a float de forma segura"""
        if pd.isna(value):
            return 0.0
        try:
            if isinstance(value, str):
                value_clean = ''.join(c for c in value if c.isdigit() or c in '.,')
                if value_clean:
                    return float(value_clean.replace(',', ''))
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _calculate_all_indicators(self, financial_data: Dict, year: int) -> Dict:
        """Calcula todos los indicadores para un año específico"""
        try:
            activo_corriente = self._safe_float(financial_data['activo_corriente'].get(year, 0))
            pasivo_corriente = self._safe_float(financial_data['pasivo_corriente'].get(year, 0))
            inventario = self._safe_float(financial_data['inventario'].get(year, 0))
            utilidad_neta = self._safe_float(financial_data['utilidad_neta'].get(year, 0))
            patrimonio = self._safe_float(financial_data['patrimonio'].get(year, 0))
            activo_total = self._safe_float(financial_data['activo_total'].get(year, 0))
            pasivo_total = self._safe_float(financial_data['pasivo_total'].get(year, 0))
            utilidad_bruta = self._safe_float(financial_data['utilidad_bruta'].get(year, 0))
            ingresos = self._safe_float(financial_data['ingresos'].get(year, 0)) or self._safe_float(financial_data['ventas'].get(year, 0))
            costo_ventas = self._safe_float(financial_data['costo_ventas'].get(year, 0))
            cuentas_por_cobrar = self._safe_float(financial_data['cuentas_por_cobrar'].get(year, 0))
            gastos_intereses = self._safe_float(financial_data['gastos_intereses'].get(year, 0))
            utilidad_antes_impuestos = self._safe_float(financial_data['utilidad_antes_impuestos'].get(year, 0))
            capital_trabajo = activo_corriente - pasivo_corriente
            
            return {
                "liquidez": self._calculate_liquidity_indicators(
                    activo_corriente, pasivo_corriente, inventario, capital_trabajo
                ),
                "rentabilidad": self._calculate_profitability_indicators(
                    utilidad_neta, patrimonio, activo_total, utilidad_bruta, ingresos
                ),
                "endeudamiento": self._calculate_debt_indicators(
                    pasivo_total, activo_total, patrimonio, utilidad_antes_impuestos, gastos_intereses
                ),
                "rotacion": self._calculate_rotation_indicators(
                    ingresos, costo_ventas, inventario, cuentas_por_cobrar, activo_total
                ),
                "quiebra": self._calculate_bankruptcy_indicators(
                    capital_trabajo, utilidad_antes_impuestos, utilidad_neta, 
                    activo_total, pasivo_total, patrimonio, ingresos
                )
            }
            
        except Exception as e:
            print(f"❌ Error calculando indicadores para {year}: {e}")
            return self._get_default_indicators()
    
    def _calculate_liquidity_indicators(self, activo_corriente, pasivo_corriente, inventario, capital_trabajo):
        razon_corriente = self._safe_divide(activo_corriente, pasivo_corriente)
        prueba_acida = self._safe_divide(activo_corriente - inventario, pasivo_corriente)
        
        clasificacion = "Crítico"
        if razon_corriente >= 1.5:
            clasificacion = "Sano"
        elif razon_corriente >= 1.0:
            clasificacion = "Regular"
        
        return {
            "razon_corriente": float(razon_corriente),
            "prueba_acida": float(prueba_acida),
            "capital_trabajo": float(capital_trabajo),
            "clasificacion_liquidez": clasificacion
        }
    
    def _calculate_profitability_indicators(self, utilidad_neta, patrimonio, activo_total, utilidad_bruta, ingresos):
        return {
            "roe": float(self._safe_divide(utilidad_neta, patrimonio)),
            "roa": float(self._safe_divide(utilidad_neta, activo_total)),
            "margen_bruto": float(self._safe_divide(utilidad_bruta, ingresos)),
            "margen_neto": float(self._safe_divide(utilidad_neta, ingresos))
        }
    
    def _calculate_debt_indicators(self, pasivo_total, activo_total, patrimonio, utilidad_antes_impuestos, gastos_intereses):
        endeudamiento_total = self._safe_divide(pasivo_total, activo_total)
        deuda_patrimonio = self._safe_divide(pasivo_total, patrimonio)
        cobertura_intereses = self._safe_divide(utilidad_antes_impuestos, gastos_intereses)
        
        clasificacion_riesgo = "Bajo"
        if endeudamiento_total > 0.6:
            clasificacion_riesgo = "Alto"
        elif endeudamiento_total > 0.4:
            clasificacion_riesgo = "Medio"
        
        return {
            "endeudamiento_total": float(endeudamiento_total),
            "deuda_patrimonio": float(deuda_patrimonio),
            "cobertura_intereses": float(cobertura_intereses),
            "clasificacion_riesgo": clasificacion_riesgo
        }
    
    def _calculate_rotation_indicators(self, ingresos, costo_ventas, inventario, cuentas_por_cobrar, activo_total):
        rotacion_inventarios = self._safe_divide(costo_ventas, inventario)
        rotacion_cartera = self._safe_divide(ingresos, cuentas_por_cobrar)
        rotacion_activos = self._safe_divide(ingresos, activo_total)
        
        dias_inventario = self._safe_divide(365, rotacion_inventarios) if rotacion_inventarios > 0 else 0
        dias_cartera = self._safe_divide(365, rotacion_cartera) if rotacion_cartera > 0 else 0
        
        return {
            "rotacion_inventarios": float(rotacion_inventarios),
            "rotacion_cartera": float(rotacion_cartera),
            "rotacion_activos": float(rotacion_activos),
            "dias_inventario": float(dias_inventario),
            "dias_cartera": float(dias_cartera)
        }
    
    def _calculate_bankruptcy_indicators(self, capital_trabajo, utilidad_antes_impuestos, utilidad_neta, 
                                        activo_total, pasivo_total, patrimonio, ingresos):
        if activo_total == 0:
            return {
                "z_score": 0.0,
                "clasificacion_z": "Sin datos",
                "probabilidad_quiebra": "Indeterminada"
            }
        
        x1 = self._safe_divide(capital_trabajo, activo_total)
        x2 = self._safe_divide(utilidad_neta, activo_total)
        x3 = self._safe_divide(utilidad_antes_impuestos, activo_total)
        x4 = self._safe_divide(patrimonio, pasivo_total)
        x5 = self._safe_divide(ingresos, activo_total)
        
        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)
        
        if z_score > 2.99:
            clasificacion = "Zona Segura"
            probabilidad = "Baja"
        elif z_score >= 1.81:
            clasificacion = "Zona Gris"
            probabilidad = "Media"
        else:
            clasificacion = "Zona de Peligro"
            probabilidad = "Alta"
        
        return {
            "z_score": float(z_score),
            "clasificacion_z": clasificacion,
            "probabilidad_quiebra": probabilidad
        }
    
    def _safe_divide(self, numerator, denominator):
        numerator = float(numerator) if numerator else 0.0
        denominator = float(denominator) if denominator else 1.0
        return numerator / denominator if denominator != 0 else 0.0
    
    def _get_default_indicators(self):
        return {
            "liquidez": {"razon_corriente": 0.0, "prueba_acida": 0.0, "capital_trabajo": 0.0, "clasificacion_liquidez": "Sin datos"},
            "rentabilidad": {"roe": 0.0, "roa": 0.0, "margen_bruto": 0.0, "margen_neto": 0.0},
            "endeudamiento": {"endeudamiento_total": 0.0, "deuda_patrimonio": 0.0, "cobertura_intereses": 0.0, "clasificacion_riesgo": "Sin datos"},
            "rotacion": {"rotacion_inventarios": 0.0, "rotacion_cartera": 0.0, "rotacion_activos": 0.0, "dias_inventario": 0, "dias_cartera": 0},
            "quiebra": {"z_score": 0.0, "clasificacion_z": "Sin datos", "probabilidad_quiebra": "Indeterminada"}
        }
    
    def _get_empty_analysis(self):
        return {
            "available_years": [],
            "indicators": {},
            "horizontal_analysis": {},
            "vertical_analysis": {}
        }
    
    def _structure_for_frontend(self, indicators_by_year: Dict, years: List[int], 
                               financial_values: Dict, horizontal_analysis: Dict, 
                               vertical_analysis: Dict) -> Dict:
        """Estructura para frontend con análisis horizontal y vertical"""
        result = {
            "available_years": sorted(years),
            "indicators": {
                "liquidez": {},
                "rentabilidad": {},
                "endeudamiento": {},
                "rotacion": {},
                "quiebra": {}
            },
            "raw_data": {},
            "horizontal_analysis": horizontal_analysis,
            "vertical_analysis": vertical_analysis
        }
        
        # Inicializar estructura de indicadores
        for indicator_type in ["liquidez", "rentabilidad", "endeudamiento", "rotacion", "quiebra"]:
            if years and years[0] in indicators_by_year:
                for indicator_name in indicators_by_year[years[0]][indicator_type].keys():
                    result["indicators"][indicator_type][indicator_name] = {}
        
        # Llenar datos por año
        for year in years:
            year_str = str(year)
            if year in indicators_by_year:
                year_data = indicators_by_year[year]
                for indicator_type, indicators_dict in year_data.items():
                    for indicator_name, value in indicators_dict.items():
                        if indicator_name not in result["indicators"][indicator_type]:
                            result["indicators"][indicator_type][indicator_name] = {}
                        
                        if isinstance(value, dict) and indicator_name != 'componentes':
                            result["indicators"][indicator_type][indicator_name][year_str] = value
                        elif not isinstance(value, dict):
                            try:
                                formatted_value = round(float(value), 4) if value else 0.0
                                result["indicators"][indicator_type][indicator_name][year_str] = formatted_value
                            except (ValueError, TypeError):
                                result["indicators"][indicator_type][indicator_name][year_str] = value
        
        # Agregar datos financieros crudos
        for concept, values in financial_values.items():
            result["raw_data"][concept] = {
                str(year): round(float(values.get(year, 0)), 2) 
                for year in years
            }
        
        print(f"\n✅ Datos estructurados: {len(result['available_years'])} años")
        print(f"📊 Análisis horizontal calculado: {len(horizontal_analysis)} cuentas")
        print(f"📊 Análisis vertical calculado: {len(vertical_analysis)} cuentas")
        
        return result