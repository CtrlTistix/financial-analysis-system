import pandas as pd
from typing import Dict, List
import numpy as np

class AnalysisService:
    def analyze_financial_data(self, df: pd.DataFrame) -> Dict:
        """Analiza datos financieros y devuelve indicadores por año"""
        
        # Verificar que tenga columna de año
        if 'Año' not in df.columns:
            # Si no tiene año, asumimos que son datos de un solo año
            df['Año'] = 2023  # O el año actual
        
        available_years = sorted(df['Año'].unique())
        indicators_by_year = {}
        
        for year in available_years:
            year_data = df[df['Año'] == year].iloc[0]
            indicators_by_year[year] = self._calculate_indicators(year_data)
        
        return self._structure_for_frontend(indicators_by_year, available_years)
    
    def _calculate_indicators(self, data) -> Dict:
        """Calcula indicadores para un año específico"""
        try:
            # Extraer valores con manejo de valores faltantes
            activo_corriente = data.get('Activo_Corriente', data.get('Activo Corriente', 0))
            pasivo_corriente = data.get('Pasivo_Corriente', data.get('Pasivo Corriente', 0))
            inventario = data.get('Inventario', data.get('Inventarios', 0))
            utilidad_neta = data.get('Utilidad_Neta', data.get('Utilidad Neta', 0))
            patrimonio = data.get('Patrimonio', 0)
            activo_total = data.get('Activo_Total', data.get('Activo Total', 0))
            utilidad_bruta = data.get('Utilidad_Bruta', data.get('Utilidad Bruta', 0))
            ingresos = data.get('Ingresos', data.get('Ventas', 1))
            
            # Cálculos de liquidez
            razon_corriente = self._safe_divide(activo_corriente, pasivo_corriente)
            prueba_acida = self._safe_divide(activo_corriente - inventario, pasivo_corriente)
            capital_trabajo = activo_corriente - pasivo_corriente
            
            # Cálculos de rentabilidad
            roe = self._safe_divide(utilidad_neta, patrimonio)
            roa = self._safe_divide(utilidad_neta, activo_total)
            margen_bruto = self._safe_divide(utilidad_bruta, ingresos)
            
            return {
                "liquidez": {
                    "razon_corriente": razon_corriente,
                    "prueba_acida": prueba_acida,
                    "capital_trabajo": capital_trabajo
                },
                "rentabilidad": {
                    "roe": roe,
                    "roa": roa,
                    "margen_bruto": margen_bruto
                }
            }
            
        except Exception as e:
            print(f"Error calculando indicadores: {e}")
            return self._get_default_indicators()
    
    def _safe_divide(self, numerator, denominator):
        """División segura evitando división por cero"""
        if denominator == 0:
            return 0
        return numerator / denominator
    
    def _get_default_indicators(self):
        """Retorna indicadores por defecto en caso de error"""
        return {
            "liquidez": {
                "razon_corriente": 0,
                "prueba_acida": 0,
                "capital_trabajo": 0
            },
            "rentabilidad": {
                "roe": 0,
                "roa": 0,
                "margen_bruto": 0
            }
        }
    
    def _structure_for_frontend(self, indicators_by_year: Dict, available_years: List[int]) -> Dict:
        """Reestructura datos para el formato que necesita el frontend"""
        result = {
            "available_years": available_years,
            "indicators": {
                "liquidez": {},
                "rentabilidad": {}
            }
        }
        
        # Inicializar estructura si hay datos
        if available_years and available_years[0] in indicators_by_year:
            for indicator_type in ["liquidez", "rentabilidad"]:
                for indicator_name in indicators_by_year[available_years[0]][indicator_type].keys():
                    result["indicators"][indicator_type][indicator_name] = {}
        
        # Llenar con datos por año
        for year in available_years:
            if year in indicators_by_year:
                for indicator_type, indicators_dict in indicators_by_year[year].items():
                    for indicator_name, value in indicators_dict.items():
                        result["indicators"][indicator_type][indicator_name][str(year)] = round(value, 2)
        
        return result