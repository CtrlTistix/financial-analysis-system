import pandas as pd
from typing import Dict, List
import numpy as np
import re

class AnalysisService:
    def analyze_financial_data(self, df: pd.DataFrame) -> Dict:
        """Analiza datos financieros con detección AUTOMÁTICA de estructura"""
        
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
        """Limpia el DataFrame SIN eliminar filas vacías iniciales"""
        print(f"\n🧹 LIMPIANDO DATAFRAME...")
        print(f"   Dimensiones iniciales: {df.shape}")
        
        # ✅ Solo eliminar columnas completamente vacías
        df = df.dropna(axis=1, how='all')
        
        # ✅ Resetear índice pero NO eliminar filas vacías
        df = df.reset_index(drop=True)
        
        # ✅ Limpiar espacios en blanco
        for col in df.columns:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        print(f"   Dimensiones finales: {df.shape}")
        return df
    
    def _find_year_row(self, df: pd.DataFrame) -> int:
        """Encuentra la fila de años SIN importar filas vacías iniciales"""
        print("\n🔎 BUSCANDO FILA DE AÑOS (Detección Inteligente)...")
        
        # ✅ Buscar en TODAS las filas, no solo desde cierto punto
        for idx, row in df.iterrows():
            year_count = 0
            years_found = []
            
            for col_idx, cell in enumerate(row):
                if pd.isna(cell):
                    continue
                
                cell_str = str(cell).strip()
                
                # ✅ BUSCAR PATRONES DE FECHA
                # Patrón: "A Julio 31 de 2016", "31/07/2016", "2016", etc.
                year_patterns = [
                    r'A\s+\w+\s+\d+\s+de\s+(20[0-2][0-9])',  # "A Julio 31 de 2016"
                    r'\b(20[0-2][0-9])\b',                      # "2016"
                    r'(\d{2})/(\d{2})/(20[0-2][0-9])',         # "31/07/2016"
                    r'(20[0-2][0-9])-\d{2}-\d{2}',             # "2016-07-31"
                ]
                
                for pattern in year_patterns:
                    matches = re.findall(pattern, cell_str)
                    if matches:
                        # Extraer solo el año
                        if isinstance(matches[0], tuple):
                            year = matches[0][-1]  # Último elemento si es tupla
                        else:
                            year = matches[0]
                        
                        if year not in years_found:
                            year_count += 1
                            years_found.append(year)
                            print(f"   Fila {idx}, Columna {col_idx}: Año detectado → {year}")
            
            # ✅ Si encontramos 2 o más años en la misma fila, ¡es la fila correcta!
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
            if pd.isna(cell):
                continue
            
            cell_str = str(cell).strip()
            
            # ✅ PATRONES MEJORADOS
            year_patterns = [
                r'A\s+\w+\s+\d+\s+de\s+(20[0-2][0-9])',  # "A Julio 31 de 2016"
                r'\b(20[0-2][0-9])\b',                      # "2016"
            ]
            
            for pattern in year_patterns:
                matches = re.findall(pattern, cell_str)
                if matches:
                    year = int(matches[0])
                    if year not in years:
                        years.append(year)
                        print(f"   Columna {col_idx}: Año {year}")
                    break
        
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
            print(f"📍 FILA DE AÑOS: {year_row_idx}")
            
            financial_values = self._extract_financial_values(df, years, year_row_idx)
            
            # ✅ VALIDAR que se encontraron datos
            has_data = any(
                any(financial_values.get(key, {}).values()) 
                for key in ['activo_total', 'pasivo_total', 'patrimonio']
            )
            
            if not has_data:
                print("⚠️ ADVERTENCIA: No se encontraron valores financieros significativos")
            
            indicators_by_year = {}
            for year in years:
                indicators_by_year[year] = self._calculate_all_indicators(financial_values, year, years)
            
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
            'capital_trabajo': {},
            'utilidad_operacional': {},
            'ebit': {},
            'depreciacion': {},
            'amortizacion': {}
        }
        
        # ✅ TÉRMINOS ADAPTADOS A TU EXCEL EXACTO
        search_terms = {
            'activo_corriente': [
                'activo corriente', 'ACTIVO CORRIENTE'
            ],
            'pasivo_corriente': [
                'pasivo corriente', 'Pasivo corriente', 'PASIVO CORRIENTE'
            ],
            'inventario': [
                'INVENTARIOS', 'inventarios', 'MERCANC', 'mercanc'
            ],
            'utilidad_neta': [
                'UTILIDAD NETA', 'utilidad neta', 'UTILIDAD O PÉRDIDA DEL EJERCICIO',
                'utilidad del ejercicio'
            ],
            'patrimonio': [
                'PATRIMONIO', 'patrimonio', 'CAPITAL SOCIAL', 'capital social'
            ],
            'activo_total': [
                'ACTIVO', 'activo'  # ← Primera línea del balance
            ],
            'pasivo_total': [
                'PASIVO', 'pasivo'  # ← No "total" porque aparece así
            ],
            'utilidad_bruta': [
                'UTILIDAD BRUTA', 'utilidad bruta'
            ],
            'ingresos': [
                'INGRESOS OPERACIONALES', 'ingresos operacionales'
            ],
            'ventas': [
                'COMERCIO AL POR MAYOR', 'comercio', 'ventas'
            ],
            'costo_ventas': [
                'COSTO DE VENTAS Y DE PRESTACIÓN', 'COSTO DE VENTAS',
                'costo de ventas'
            ],
            'cuentas_por_cobrar': [
                'CLIENTES', 'clientes', 'DEUDORES', 'deudores'  # ← CLAVE
            ],
            'gastos_intereses': [
                'Intereses', 'intereses', 'FINANCIEROS', 'Gastos bancarios'
            ],
            'utilidad_operacional': [
                'UTILIDAD OPERACIONAL', 'utilidad operacional'
            ],
        }
        
        print(f"\n🔍 EXTRAYENDO VALORES FINANCIEROS...")
        print(f"   Buscando desde fila {year_row_idx + 1} en adelante")
        
        for year in years:
            year_col_idx = self._find_year_column(df, year, year_row_idx)
            if year_col_idx is not None:
                print(f"\n   📅 Año {year} → Columna {year_col_idx}")
                for concept, terms in search_terms.items():
                    value = self._find_concept_value(df, terms, year_col_idx, year_row_idx)
                    financial_data[concept][year] = value
                    if value != 0:
                        print(f"      ✓ {concept}: ${value:,.2f}")
                    else:
                        print(f"      ⚠️ {concept}: NO ENCONTRADO (buscando: {terms[0]})")
        
        return financial_data
    
    def _find_year_column(self, df: pd.DataFrame, year: int, year_row_idx: int) -> int:
        """Encuentra la columna para un año específico"""
        row = df.iloc[year_row_idx]
        for col_idx, cell in enumerate(row):
            if pd.isna(cell):
                continue
            cell_str = str(cell)
            if str(year) in cell_str:
                return col_idx
        return None
    
    def _find_concept_value(self, df: pd.DataFrame, search_terms: List[str], year_col: int, year_row: int) -> float:
        """Encuentra el valor de un concepto financiero CON BÚSQUEDA INTELIGENTE"""
        
        # ✅ BUSCAR DESDE LA FILA SIGUIENTE A LOS AÑOS
        for idx in range(year_row + 1, len(df)):
            row = df.iloc[idx]
            
            # ✅ Buscar en las primeras 10 columnas (ampliado)
            search_range = min(10, len(row))
            
            for col_idx in range(search_range):
                if col_idx >= len(row):
                    break
                
                cell = row.iloc[col_idx]
                if pd.isna(cell):
                    continue
                
                cell_str = str(cell).strip().upper()  # ← MAYÚSCULAS para comparación
                
                # ✅ Buscar cada término
                for term in search_terms:
                    term_upper = term.upper()
                    
                    # ✅ COINCIDENCIA EXACTA o que EMPIECE con el término
                    if cell_str == term_upper or cell_str.startswith(term_upper):
                        # ✅ ENCONTRADO - Extraer valor de la columna del año
                        if year_col >= len(row):
                            return 0.0
                        
                        value = row.iloc[year_col]
                        return self._parse_value(value)
        
        # No encontrado
        return 0.0
    
    def _parse_value(self, value) -> float:
        """Convierte cualquier formato de número a float"""
        try:
            if pd.isna(value):
                return 0.0
            
            if isinstance(value, (int, float)):
                return float(value)
            
            if isinstance(value, str):
                # Limpiar el valor
                value_clean = value.replace('$', '').replace(' ', '').strip()
                
                # Manejar valores negativos entre paréntesis: (1.000) → -1000
                if '(' in value_clean and ')' in value_clean:
                    value_clean = '-' + value_clean.replace('(', '').replace(')', '')
                
                # Remover puntos de miles y reemplazar coma decimal por punto
                # Ej: "1.229.499.222,08" → "1229499222.08"
                if ',' in value_clean:
                    value_clean = value_clean.replace('.', '').replace(',', '.')
                else:
                    # Si no hay coma, solo quitar puntos de miles
                    value_clean = value_clean.replace(',', '')
                
                if value_clean and value_clean not in ['-', '', '.']:
                    return float(value_clean)
                
            return 0.0
            
        except (ValueError, TypeError) as e:
            print(f"   ⚠️ Error parseando valor '{value}': {e}")
            return 0.0
    
    def _safe_float(self, value):
        """Convierte valores a float de forma segura"""
        return self._parse_value(value)
    
    def _calculate_all_indicators(self, financial_data: Dict, year: int, years: List[int]) -> Dict:
        """Calcula todos los indicadores para un año específico"""
        try:
            years_sorted = sorted(years)
            year_index = years_sorted.index(year)
            
            # ✅ CALCULAR PROMEDIOS SI HAY AÑO ANTERIOR
            if year_index > 0:
                previous_year = years_sorted[year_index - 1]
                
                # Promedio de Patrimonio
                patrimonio_actual = self._safe_float(financial_data['patrimonio'].get(year, 0))
                patrimonio_anterior = self._safe_float(financial_data['patrimonio'].get(previous_year, 0))
                patrimonio_promedio = (patrimonio_actual + patrimonio_anterior) / 2 if patrimonio_anterior > 0 else patrimonio_actual
                
                # Promedio de Activo Total
                activo_actual = self._safe_float(financial_data['activo_total'].get(year, 0))
                activo_anterior = self._safe_float(financial_data['activo_total'].get(previous_year, 0))
                activo_promedio = (activo_actual + activo_anterior) / 2 if activo_anterior > 0 else activo_actual
                
                # Promedio de Inventario
                inventario_actual = self._safe_float(financial_data['inventario'].get(year, 0))
                inventario_anterior = self._safe_float(financial_data['inventario'].get(previous_year, 0))
                inventario_promedio = (inventario_actual + inventario_anterior) / 2 if inventario_anterior > 0 else inventario_actual
                
                # Promedio de Cuentas por Cobrar
                cxc_actual = self._safe_float(financial_data['cuentas_por_cobrar'].get(year, 0))
                cxc_anterior = self._safe_float(financial_data['cuentas_por_cobrar'].get(previous_year, 0))
                cxc_promedio = (cxc_actual + cxc_anterior) / 2 if cxc_anterior > 0 else cxc_actual
            else:
                patrimonio_promedio = self._safe_float(financial_data['patrimonio'].get(year, 0))
                activo_promedio = self._safe_float(financial_data['activo_total'].get(year, 0))
                inventario_promedio = self._safe_float(financial_data['inventario'].get(year, 0))
                cxc_promedio = self._safe_float(financial_data['cuentas_por_cobrar'].get(year, 0))
            
            # Variables del año actual
            activo_corriente = self._safe_float(financial_data['activo_corriente'].get(year, 0))
            pasivo_corriente = self._safe_float(financial_data['pasivo_corriente'].get(year, 0))
            inventario = self._safe_float(financial_data['inventario'].get(year, 0))
            utilidad_neta = self._safe_float(financial_data['utilidad_neta'].get(year, 0))
            activo_total = self._safe_float(financial_data['activo_total'].get(year, 0))
            pasivo_total = self._safe_float(financial_data['pasivo_total'].get(year, 0))
            patrimonio = self._safe_float(financial_data['patrimonio'].get(year, 0))
            utilidad_bruta = self._safe_float(financial_data['utilidad_bruta'].get(year, 0))
            ingresos = self._safe_float(financial_data['ingresos'].get(year, 0)) or self._safe_float(financial_data['ventas'].get(year, 0))
            costo_ventas = self._safe_float(financial_data['costo_ventas'].get(year, 0))
            cuentas_por_cobrar = self._safe_float(financial_data['cuentas_por_cobrar'].get(year, 0))
            gastos_intereses = self._safe_float(financial_data['gastos_intereses'].get(year, 0))
            utilidad_operacional = self._safe_float(financial_data['utilidad_operacional'].get(year, 0))
            capital_trabajo = activo_corriente - pasivo_corriente
            
            print(f"\n📊 CALCULANDO INDICADORES PARA {year}:")
            print(f"   Activo Total (promedio): ${activo_promedio:,.2f}")
            print(f"   Ingresos: ${ingresos:,.2f}")
            print(f"   CxC (promedio): ${cxc_promedio:,.2f}")
            print(f"   Inventario (promedio): ${inventario_promedio:,.2f}")
            
            return {
                "liquidez": self._calculate_liquidity_indicators(
                    activo_corriente, pasivo_corriente, inventario, capital_trabajo
                ),
                "rentabilidad": self._calculate_profitability_indicators(
                    utilidad_neta, patrimonio_promedio, activo_promedio, utilidad_bruta, ingresos
                ),
                "endeudamiento": self._calculate_debt_indicators(
                    pasivo_total, activo_total, patrimonio, utilidad_operacional, gastos_intereses
                ),
                "rotacion": self._calculate_rotation_indicators(
                    ingresos, costo_ventas, inventario_promedio, cxc_promedio, activo_promedio
                ),
                "quiebra": self._calculate_bankruptcy_indicators(
                    capital_trabajo, utilidad_operacional, utilidad_neta, 
                    activo_total, pasivo_total, patrimonio, ingresos
                )
            }
            
        except Exception as e:
            print(f"❌ Error calculando indicadores para {year}: {e}")
            import traceback
            traceback.print_exc()
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
            "razon_corriente": round(float(razon_corriente), 4),
            "prueba_acida": round(float(prueba_acida), 4),
            "capital_trabajo": round(float(capital_trabajo), 2),
            "clasificacion_liquidez": clasificacion
        }
    
    def _calculate_profitability_indicators(self, utilidad_neta, patrimonio_promedio, activo_promedio, utilidad_bruta, ingresos):
        return {
            "roe": round(float(self._safe_divide(utilidad_neta, patrimonio_promedio)), 4),
            "roa": round(float(self._safe_divide(utilidad_neta, activo_promedio)), 4),
            "margen_bruto": round(float(self._safe_divide(utilidad_bruta, ingresos)), 4),
            "margen_neto": round(float(self._safe_divide(utilidad_neta, ingresos)), 4)
        }
    
    def _calculate_debt_indicators(self, pasivo_total, activo_total, patrimonio, utilidad_operacional, gastos_intereses):
        endeudamiento_total = self._safe_divide(pasivo_total, activo_total)
        deuda_patrimonio = self._safe_divide(pasivo_total, patrimonio)
        cobertura_intereses = self._safe_divide(utilidad_operacional, gastos_intereses)
        
        clasificacion_riesgo = "Bajo"
        if endeudamiento_total > 0.6:
            clasificacion_riesgo = "Alto"
        elif endeudamiento_total > 0.4:
            clasificacion_riesgo = "Medio"
        
        return {
            "endeudamiento_total": round(float(endeudamiento_total), 4),
            "deuda_patrimonio": round(float(deuda_patrimonio), 4),
            "cobertura_intereses": round(float(cobertura_intereses), 4),
            "clasificacion_riesgo": clasificacion_riesgo
        }
    
    def _calculate_rotation_indicators(self, ingresos, costo_ventas, inventario_promedio, cuentas_por_cobrar_promedio, activo_total_promedio):
        """Calcula indicadores de rotación con validaciones ULTRA ROBUSTAS"""
        
        print(f"\n🔄 CALCULANDO INDICADORES DE ROTACIÓN...")
        print(f"   Ingresos: ${ingresos:,.2f}")
        print(f"   Costo Ventas: ${costo_ventas:,.2f}")
        print(f"   Inventario Promedio: ${inventario_promedio:,.2f}")
        print(f"   CxC Promedio: ${cuentas_por_cobrar_promedio:,.2f}")
        print(f"   Activo Total Promedio: ${activo_total_promedio:,.2f}")
        
        # Rotación de Inventarios
        if inventario_promedio > 1 and costo_ventas > 0:
            rotacion_inventarios = costo_ventas / inventario_promedio
            dias_inventario = 365 / rotacion_inventarios
            print(f"   ✅ Rotación Inventarios: {rotacion_inventarios:.2f} veces/año")
            print(f"   ✅ Días Inventario: {dias_inventario:.2f} días")
        else:
            rotacion_inventarios = 0.0
            dias_inventario = 0.0
            print(f"   ⚠️ Rotación Inventarios: NO calculable (Inventario = ${inventario_promedio:,.2f})")
        
        # Rotación de Cartera
        if cuentas_por_cobrar_promedio > 1 and ingresos > 0:
            rotacion_cartera = ingresos / cuentas_por_cobrar_promedio
            dias_cartera = 365 / rotacion_cartera
            print(f"   ✅ Rotación Cartera: {rotacion_cartera:.2f} veces/año")
            print(f"   ✅ Días Cartera: {dias_cartera:.2f} días")
        else:
            rotacion_cartera = 0.0
            dias_cartera = 0.0
            print(f"   ⚠️ Rotación Cartera: NO calculable (CxC = ${cuentas_por_cobrar_promedio:,.2f})")
        
        # Rotación de Activos
        if activo_total_promedio > 1 and ingresos > 0:
            rotacion_activos = ingresos / activo_total_promedio
            print(f"   ✅ Rotación Activos: {rotacion_activos:.2f} veces/año")
        else:
            rotacion_activos = 0.0
            print(f"   ⚠️ Rotación Activos: NO calculable")
        
        # ✅ VALIDAR QUE LOS VALORES SEAN RAZONABLES
        if dias_inventario > 3650:  # Más de 10 años
            print(f"   ❌ ERROR: Días inventario anormales ({dias_inventario:.0f}), ajustando a 0")
            dias_inventario = 0.0
            rotacion_inventarios = 0.0
        
        if dias_cartera > 3650:  # Más de 10 años
            print(f"   ❌ ERROR: Días cartera anormales ({dias_cartera:.0f}), ajustando a 0")
            dias_cartera = 0.0
            rotacion_cartera = 0.0
        
        if rotacion_activos > 100:
            print(f"   ⚠️ ADVERTENCIA: Rotación activos muy alta ({rotacion_activos:.2f})")
        
        return {
            "rotacion_inventarios": round(float(rotacion_inventarios), 4),
            "rotacion_cartera": round(float(rotacion_cartera), 4),
            "rotacion_activos": round(float(rotacion_activos), 4),
            "dias_inventario": round(float(dias_inventario), 2),
            "dias_cartera": round(float(dias_cartera), 2)
        }
    
    def _calculate_bankruptcy_indicators(self, capital_trabajo, utilidad_operacional, utilidad_neta, 
                                        activo_total, pasivo_total, patrimonio, ingresos):
        if activo_total == 0:
            return {
                "z_score": 0.0,
                "clasificacion_z": "Sin datos",
                "probabilidad_quiebra": "Indeterminada"
            }
        
        # ✅ FÓRMULA CORRECTA DEL Z-SCORE DE ALTMAN
        x1 = self._safe_divide(capital_trabajo, activo_total)
        x2 = self._safe_divide(utilidad_neta, activo_total)
        x3 = self._safe_divide(utilidad_operacional, activo_total)  # EBIT
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
            "z_score": round(float(z_score), 4),
            "clasificacion_z": clasificacion,
            "probabilidad_quiebra": probabilidad
        }
    
    def _calculate_horizontal_analysis(self, financial_values: Dict, years: List[int]) -> Dict:
        """Calcula análisis horizontal (variaciones entre períodos)"""
        print("\n📈 CALCULANDO ANÁLISIS HORIZONTAL...")
        
        horizontal = {}
        
        main_accounts = [
            'activo_corriente', 'activo_total', 'pasivo_corriente', 
            'pasivo_total', 'patrimonio', 'ingresos', 'ventas',
            'costo_ventas', 'utilidad_bruta', 'utilidad_neta',
            'inventario', 'cuentas_por_cobrar'
        ]
        
        for account in main_accounts:
            if account not in financial_values:
                continue
            
            has_values = any(abs(financial_values[account].get(year, 0)) > 0.01 for year in years)
            if not has_values:
                print(f"   ⚠️ {account}: Sin valores, se omite")
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
                    
                    absolute_var = current_value - previous_value
                    horizontal[account]['absolute_variation'][str(year)] = absolute_var
                    
                    if previous_value != 0:
                        percentage_var = ((current_value - previous_value) / previous_value) * 100
                    else:
                        percentage_var = 0 if current_value == 0 else 100.0
                    horizontal[account]['percentage_variation'][str(year)] = percentage_var
                    
                    print(f"   {account} {year}: ${current_value:,.0f} ({percentage_var:+.1f}%)")
        
        return horizontal
    
    def _calculate_vertical_analysis(self, financial_values: Dict, years: List[int]) -> Dict:
        """Calcula análisis vertical (estructura porcentual)"""
        print("\n📊 CALCULANDO ANÁLISIS VERTICAL...")
        
        vertical = {}
        
        if 'activo_total' not in financial_values:
            print("   ❌ No se puede calcular: falta Activo Total")
            return vertical
        
        balance_accounts = [
            'activo_corriente', 'activo_total', 'pasivo_corriente',
            'pasivo_total', 'patrimonio', 'inventario', 'cuentas_por_cobrar'
        ]
        
        for account in balance_accounts:
            if account not in financial_values:
                continue
            
            has_values = any(abs(financial_values[account].get(year, 0)) > 0.01 for year in years)
            if not has_values and account != 'activo_total':
                continue
            
            vertical[account] = {}
            
            for year in years:
                account_value = financial_values[account].get(year, 0)
                activo_total = financial_values['activo_total'].get(year, 0)
                
                if activo_total != 0:
                    if account == 'activo_total':
                        percentage = 100.0
                    else:
                        percentage = (account_value / activo_total) * 100
                else:
                    percentage = 0.0
                
                vertical[account][str(year)] = round(percentage, 2)
                
                if percentage != 0:
                    print(f"   {account} {year}: {percentage:.1f}%")
        
        # Análisis del Estado de Resultados
        income_accounts = [
            'ingresos', 'ventas', 'costo_ventas', 'utilidad_bruta', 
            'utilidad_neta'
        ]
        
        for account in income_accounts:
            if account not in financial_values:
                continue
            
            has_values = any(abs(financial_values[account].get(year, 0)) > 0.01 for year in years)
            if not has_values and account not in ['ingresos', 'ventas']:
                continue
            
            if account not in vertical:
                vertical[account] = {}
            
            for year in years:
                account_value = financial_values[account].get(year, 0)
                ingresos = financial_values.get('ingresos', {}).get(year, 0) or financial_values.get('ventas', {}).get(year, 0)
                
                if ingresos != 0:
                    if account in ['ingresos', 'ventas']:
                        percentage = 100.0
                    else:
                        percentage = (account_value / ingresos) * 100
                else:
                    percentage = 0.0
                
                vertical[account][str(year)] = round(percentage, 2)
        
        return vertical
    
    def _safe_divide(self, numerator, denominator):
        """División segura"""
        try:
            numerator = float(numerator) if numerator else 0.0
            denominator = float(denominator) if denominator else 0.0
            
            if denominator == 0:
                return 0.0
            
            result = numerator / denominator
            
            if abs(result) > 1e10:
                return 0.0
            
            return result
        except:
            return 0.0
    
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
            "vertical_analysis": {},
            "raw_data": {}
        }
    
    def _structure_for_frontend(self, indicators_by_year: Dict, years: List[int], 
                               financial_values: Dict, horizontal_analysis: Dict, 
                               vertical_analysis: Dict) -> Dict:
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
            "raw_data": {},
            "horizontal_analysis": horizontal_analysis,
            "vertical_analysis": vertical_analysis
        }
        
        for indicator_type in ["liquidez", "rentabilidad", "endeudamiento", "rotacion", "quiebra"]:
            if years and years[0] in indicators_by_year:
                for indicator_name in indicators_by_year[years[0]][indicator_type].keys():
                    result["indicators"][indicator_type][indicator_name] = {}
        
        for year in years:
            year_str = str(year)
            if year in indicators_by_year:
                year_data = indicators_by_year[year]
                for indicator_type, indicators_dict in year_data.items():
                    for indicator_name, value in indicators_dict.items():
                        if indicator_name not in result["indicators"][indicator_type]:
                            result["indicators"][indicator_type][indicator_name] = {}
                        
                        if isinstance(value, dict):
                            result["indicators"][indicator_type][indicator_name][year_str] = value
                        else:
                            try:
                                if isinstance(value, (int, float)):
                                    formatted_value = round(float(value), 4)
                                else:
                                    formatted_value = value
                                result["indicators"][indicator_type][indicator_name][year_str] = formatted_value
                            except:
                                result["indicators"][indicator_type][indicator_name][year_str] = value
        
        for concept, values in financial_values.items():
            result["raw_data"][concept] = {
                str(year): round(float(values.get(year, 0)), 2) 
                for year in years
            }
        
        print(f"\n✅ Datos estructurados: {len(result['available_years'])} años")
        print(f"📊 Análisis horizontal: {len(horizontal_analysis)} cuentas")
        print(f"📊 Análisis vertical: {len(vertical_analysis)} cuentas")
        
        return result