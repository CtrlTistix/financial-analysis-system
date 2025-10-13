import pandas as pd
from typing import Dict, List
import numpy as np

class AnalysisService:
    def analyze_financial_data(self, df: pd.DataFrame) -> Dict:
        """Analiza datos financieros con detección mejorada"""
        
        print(f"🔍 Iniciando análisis con {len(df.columns)} columnas")
        
        # Limpiar el DataFrame
        df_clean = self._clean_dataframe(df)
        
        # Detectar años y estructura
        analysis_result = self._analyze_data_structure(df_clean)
        
        if not analysis_result['success']:
            return self._get_empty_analysis()
        
        print(f"✅ Estructura detectada: {analysis_result}")
        return analysis_result['data']
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y prepara el DataFrame"""
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # Eliminar columnas completamente vacías
        df = df.dropna(axis=1, how='all')
        
        # Resetear índice
        df = df.reset_index(drop=True)
        
        return df
    
    def _analyze_data_structure(self, df: pd.DataFrame) -> Dict:
        """Analiza la estructura del DataFrame y extrae datos"""
        try:
            # Buscar fila con años
            year_row_idx = self._find_year_row(df)
            if year_row_idx is None:
                return {'success': False, 'error': 'No se encontraron años'}
            
            # Extraer años
            years = self._extract_years_from_row(df, year_row_idx)
            if not years:
                return {'success': False, 'error': 'No se pudieron extraer años'}
            
            print(f"📅 Años detectados: {years}")
            
            # Buscar valores financieros
            financial_values = self._extract_financial_values(df, years, year_row_idx)
            
            # Calcular indicadores
            indicators_by_year = {}
            for year in years:
                indicators_by_year[year] = self._calculate_indicators(financial_values, year)
            
            return {
                'success': True,
                'data': self._structure_for_frontend(indicators_by_year, years)
            }
            
        except Exception as e:
            print(f"❌ Error en análisis de estructura: {e}")
            return {'success': False, 'error': str(e)}
    
    def _find_year_row(self, df: pd.DataFrame) -> int:
        """Encuentra la fila que contiene los años"""
        for idx, row in df.iterrows():
            for cell in row:
                cell_str = str(cell).lower()
                # Buscar patrones de año
                if any(str(year) in cell_str for year in range(2000, 2030)):
                    return idx
        return None
    
    def _extract_years_from_row(self, df: pd.DataFrame, row_idx: int) -> List[int]:
        """Extrae años de una fila específica"""
        years = []
        row = df.iloc[row_idx]
        
        for cell in row:
            cell_str = str(cell)
            # Buscar años en el texto de la celda
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
            'utilidad_bruta': {},
            'ingresos': {}
        }
        
        # Mapeo de términos de búsqueda
        search_terms = {
            'activo_corriente': ['activo corriente', 'activos corrientes'],
            'pasivo_corriente': ['pasivo corriente', 'pasivos corrientes'],
            'inventario': ['inventario', 'inventarios'],
            'utilidad_neta': ['utilidad neta', 'utilidad del ejercicio'],
            'patrimonio': ['patrimonio', 'capital'],
            'activo_total': ['activo total', 'total activo'],
            'utilidad_bruta': ['utilidad bruta'],
            'ingresos': ['ingresos', 'ventas']
        }
        
        # Buscar valores para cada año
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
            if idx <= year_row:  # Buscar después de la fila de años
                continue
                
            for cell in row:
                if pd.notna(cell) and any(term in str(cell).lower() for term in search_terms):
                    # Encontrado el concepto, tomar valor de la columna del año
                    value = row[year_col]
                    try:
                        return float(value) if pd.notna(value) else 0.0
                    except:
                        return 0.0
        return 0.0
    
    def _calculate_indicators(self, financial_data: Dict, year: int) -> Dict:
        """Calcula indicadores para un año específico"""
        try:
            # Extraer valores
            activo_corriente = financial_data['activo_corriente'].get(year, 0)
            pasivo_corriente = financial_data['pasivo_corriente'].get(year, 0)
            inventario = financial_data['inventario'].get(year, 0)
            utilidad_neta = financial_data['utilidad_neta'].get(year, 0)
            patrimonio = financial_data['patrimonio'].get(year, 0)
            activo_total = financial_data['activo_total'].get(year, 0)
            utilidad_bruta = financial_data['utilidad_bruta'].get(year, 0)
            ingresos = financial_data['ingresos'].get(year, 0)
            
            print(f"📊 Valores para {year}: AC={activo_corriente}, PC={pasivo_corriente}")
            
            # Cálculos
            razon_corriente = self._safe_divide(activo_corriente, pasivo_corriente)
            prueba_acida = self._safe_divide(activo_corriente - inventario, pasivo_corriente)
            capital_trabajo = activo_corriente - pasivo_corriente
            roe = self._safe_divide(utilidad_neta, patrimonio)
            roa = self._safe_divide(utilidad_neta, activo_total)
            margen_bruto = self._safe_divide(utilidad_bruta, ingresos)
            
            return {
                "liquidez": {
                    "razon_corriente": float(razon_corriente),
                    "prueba_acida": float(prueba_acida),
                    "capital_trabajo": float(capital_trabajo)
                },
                "rentabilidad": {
                    "roe": float(roe),
                    "roa": float(roa),
                    "margen_bruto": float(margen_bruto)
                }
            }
            
        except Exception as e:
            print(f"❌ Error calculando indicadores: {e}")
            return self._get_default_indicators()
    
    def _safe_divide(self, numerator, denominator):
        """División segura"""
        numerator = float(numerator) if numerator else 0.0
        denominator = float(denominator) if denominator else 1.0
        return numerator / denominator if denominator != 0 else 0.0
    
    def _get_default_indicators(self):
        """Indicadores por defecto"""
        return {
            "liquidez": {"razon_corriente": 0.0, "prueba_acida": 0.0, "capital_trabajo": 0.0},
            "rentabilidad": {"roe": 0.0, "roa": 0.0, "margen_bruto": 0.0}
        }
    
    def _get_empty_analysis(self):
        """Análisis vacío"""
        return {
            "available_years": [],
            "indicators": {"liquidez": {}, "rentabilidad": {}}
        }
    
    def _structure_for_frontend(self, indicators_by_year: Dict, years: List[int]) -> Dict:
        """Estructura para frontend"""
        result = {
            "available_years": sorted(years),
            "indicators": {"liquidez": {}, "rentabilidad": {}}
        }
        
        # Inicializar estructura
        for indicator_type in ["liquidez", "rentabilidad"]:
            if years and years[0] in indicators_by_year:
                for indicator_name in indicators_by_year[years[0]][indicator_type].keys():
                    result["indicators"][indicator_type][indicator_name] = {}
        
        # Llenar datos
        for year in years:
            if year in indicators_by_year:
                year_data = indicators_by_year[year]
                for indicator_type, indicators_dict in year_data.items():
                    for indicator_name, value in indicators_dict.items():
                        result["indicators"][indicator_type][indicator_name][str(year)] = round(float(value), 2)
        
        print(f"✅ Datos estructurados: {len(result['available_years'])} años")
        return result