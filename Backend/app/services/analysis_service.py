import pandas as pd
from typing import Dict, List
import numpy as np

class AnalysisService:
    def analyze_financial_data(self, df: pd.DataFrame) -> Dict:
        """Analiza datos financieros con detección mejorada"""
        
        print(f"🔍 Iniciando análisis con {len(df.columns)} columnas")
        
        df_clean = self._clean_dataframe(df)
        analysis_result = self._analyze_data_structure(df_clean)
        
        if not analysis_result['success']:
            return self._get_empty_analysis()
        
        print(f"✅ Estructura detectada")
        return analysis_result['data']
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y prepara el DataFrame"""
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        df = df.reset_index(drop=True)
        return df
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict:
        """Analiza la estructura del DataFrame y extrae datos"""
        try:
            year_row_idx = self._find_year_row(df)
            if year_row_idx is None:
                return {'success': False, 'error': 'No se encontraron años'}
            
            years = self._extract_years_from_row(df, year_row_idx)
            if not years:
                return {'success': False, 'error': 'No se pudieron extraer años'}
            
            print(f"📅 Años detectados: {years}")
            
            financial_values = self._extract_financial_values(df, years, year_row_idx)
            
            indicators_by_year = {}
            for year in years:
                indicators_by_year[year] = self._calculate_all_indicators(financial_values, year)
            
            return {
                'success': True,
                'data': self._structure_for_frontend(indicators_by_year, years, financial_values)
            }
            
        except Exception as e:
            print(f"❌ Error en análisis de estructura: {e}")
            return {'success': False, 'error': str(e)}
    
    def _find_year_row(self, df: pd.DataFrame) -> int:
        """Encuentra la fila que contiene los años"""
        for idx, row in df.iterrows():
            for cell in row:
                cell_str = str(cell).lower()
                if any(str(year) in cell_str for year in range(2000, 2030)):
                    return idx
        return None
    
    def _extract_years_from_row(self, df: pd.DataFrame, row_idx: int) -> List[int]:
        """Extrae años de una fila específica"""
        years = []
        row = df.iloc[row_idx]
        
        for cell in row:
            cell_str = str(cell)
            for year in range(2000, 2030):
                if str(year) in cell_str:
                    years.append(year)
                    break
        
        return sorted(list(set(years)))
    
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
            'activo_corriente': ['activo corriente', 'activos corrientes'],
            'pasivo_corriente': ['pasivo corriente', 'pasivos corrientes'],
            'inventario': ['inventario', 'inventarios'],
            'utilidad_neta': ['utilidad neta', 'utilidad del ejercicio', 'resultado neto'],
            'patrimonio': ['patrimonio', 'capital', 'patrimonio neto'],
            'activo_total': ['activo total', 'total activo', 'total de activos'],
            'pasivo_total': ['pasivo total', 'total pasivo', 'total de pasivos'],
            'utilidad_bruta': ['utilidad bruta', 'beneficio bruto'],
            'ingresos': ['ingresos', 'ingresos operacionales'],
            'ventas': ['ventas', 'ventas netas'],
            'costo_ventas': ['costo de ventas', 'costo ventas'],
            'cuentas_por_cobrar': ['cuentas por cobrar', 'clientes', 'deudores'],
            'gastos_intereses': ['gastos financieros', 'intereses', 'gastos por intereses'],
            'utilidad_antes_impuestos': ['utilidad antes de impuestos', 'ebt'],
            'capital_trabajo': ['capital de trabajo', 'working capital']
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
            if str(year) in str(cell):
                return col_idx
        return None
    
    def _find_concept_value(self, df: pd.DataFrame, search_terms: List[str], year_col: int, year_row: int) -> float:
        """Encuentra el valor de un concepto financiero"""
        for idx, row in df.iterrows():
            if idx <= year_row:
                continue
                
            for cell in row:
                if pd.notna(cell) and any(term in str(cell).lower() for term in search_terms):
                    value = row[year_col]
                    try:
                        if isinstance(value, str):
                            value_clean = ''.join(c for c in value if c.isdigit() or c in '.,')
                            if value_clean:
                                return float(value_clean.replace(',', ''))
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
            
            print(f"📊 Valores para {year}: AC={activo_corriente}, PC={pasivo_corriente}")
            
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
            print(f"❌ Error calculando indicadores: {e}")
            return self._get_default_indicators()
    
    def _calculate_liquidity_indicators(self, activo_corriente, pasivo_corriente, inventario, capital_trabajo):
        """Indicadores de liquidez"""
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
        """Indicadores de rentabilidad"""
        return {
            "roe": float(self._safe_divide(utilidad_neta, patrimonio)),
            "roa": float(self._safe_divide(utilidad_neta, activo_total)),
            "margen_bruto": float(self._safe_divide(utilidad_bruta, ingresos)),
            "margen_neto": float(self._safe_divide(utilidad_neta, ingresos))
        }
    
    def _calculate_debt_indicators(self, pasivo_total, activo_total, patrimonio, utilidad_antes_impuestos, gastos_intereses):
        """Indicadores de endeudamiento"""
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
        """Indicadores de rotación"""
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
        """Indicadores de quiebra - Z-Score de Altman"""
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
            "probabilidad_quiebra": probabilidad,
            "componentes": {
                "capital_trabajo_activos": float(x1),
                "utilidades_retenidas_activos": float(x2),
                "ebit_activos": float(x3),
                "patrimonio_pasivos": float(x4),
                "ventas_activos": float(x5)
            }
        }
    
    def _safe_divide(self, numerator, denominator):
        """División segura"""
        numerator = float(numerator) if numerator else 0.0
        denominator = float(denominator) if denominator else 1.0
        return numerator / denominator if denominator != 0 else 0.0
    
    def _get_default_indicators(self):
        """Indicadores por defecto"""
        return {
            "liquidez": {"razon_corriente": 0.0, "prueba_acida": 0.0, "capital_trabajo": 0.0, "clasificacion_liquidez": "Sin datos"},
            "rentabilidad": {"roe": 0.0, "roa": 0.0, "margen_bruto": 0.0, "margen_neto": 0.0},
            "endeudamiento": {"endeudamiento_total": 0.0, "deuda_patrimonio": 0.0, "cobertura_intereses": 0.0, "clasificacion_riesgo": "Sin datos"},
            "rotacion": {"rotacion_inventarios": 0.0, "rotacion_cartera": 0.0, "rotacion_activos": 0.0, "dias_inventario": 0, "dias_cartera": 0},
            "quiebra": {"z_score": 0.0, "clasificacion_z": "Sin datos", "probabilidad_quiebra": "Indeterminada"}
        }
    
    def _get_empty_analysis(self):
        """Análisis vacío"""
        return {
            "available_years": [],
            "indicators": {
                "liquidez": {},
                "rentabilidad": {},
                "endeudamiento": {},
                "rotacion": {},
                "quiebra": {}
            }
        }
    
    def _structure_for_frontend(self, indicators_by_year: Dict, years: List[int], financial_values: Dict) -> Dict:
        """Estructura para frontend"""
        result = {
            "available_years": sorted(years),
            "indicators": {
                "liquidez": {},
                "rentabilidad": {},
                "endeudamiento": {},
                "rotacion": {},
                "quiebra": {}
            },
            "raw_data": {}
        }
        
        for indicator_type in ["liquidez", "rentabilidad", "endeudamiento", "rotacion", "quiebra"]:
            if years and years[0] in indicators_by_year:
                for indicator_name in indicators_by_year[years[0]][indicator_type].keys():
                    result["indicators"][indicator_type][indicator_name] = {}
        
        for year in years:
            if year in indicators_by_year:
                year_data = indicators_by_year[year]
                for indicator_type, indicators_dict in year_data.items():
                    for indicator_name, value in indicators_dict.items():
                        if isinstance(value, dict):
                            result["indicators"][indicator_type][indicator_name][str(year)] = value
                        else:
                            result["indicators"][indicator_type][indicator_name][str(year)] = round(float(value), 2)
        
        for concept, values in financial_values.items():
            result["raw_data"][concept] = {str(year): values.get(year, 0) for year in years}
        
        print(f"✅ Datos estructurados: {len(result['available_years'])} años")
        return result