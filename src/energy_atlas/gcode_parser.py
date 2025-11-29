import math
import re
from typing import Dict, List, Any, Tuple

class GCodeEnergyParser:
    """
    Parses G-code to estimate thermodynamic energy expenditure.
    
    Model:
    - Kinetic Energy: Based on stepper motor power and movement duration.
    - Thermal Energy: Based on heater power required to maintain/reach temp.
    - Latent Energy: Energy required to melt the filament.
    """
    
    # Default Printer Specs (Prusa i3 MK3S+ approximation)
    SPECS = {
        'nozzle_heater_power_w': 40.0,
        'bed_heater_power_w': 200.0,
        'stepper_power_w': 5.0, # Per axis
        'filament_diameter_mm': 1.75,
        'filament_density_g_cm3': 1.24, # PLA
        'filament_heat_capacity_j_g_k': 1.8, # PLA
        'filament_heat_fusion_j_g': 0.0, # Amorphous (glass transition), but simplified
        'ambient_temp_c': 25.0
    }

    def __init__(self, specs: Dict[str, float] = None):
        self.specs = specs or self.SPECS
        self.current_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'E': 0.0}
        self.current_temp = {'nozzle': 25.0, 'bed': 25.0}
        self.target_temp = {'nozzle': 0.0, 'bed': 0.0}
        self.feedrate_mm_min = 1000.0
        self.total_energy_j = 0.0
        self.total_time_s = 0.0
        self.layers = []

    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Parse a G-code file and return energy metrics."""
        with open(filepath, 'r') as f:
            lines = f.readlines()

        for line in lines:
            self._process_line(line)
            
        return {
            'total_energy_joules': self.total_energy_j,
            'total_time_seconds': self.total_time_s,
            'average_power_watts': self.total_energy_j / self.total_time_s if self.total_time_s > 0 else 0,
            'layers': len(self.layers)
        }

    def _process_line(self, line: str):
        line = line.split(';')[0].strip().upper() # Remove comments
        if not line:
            return

        parts = line.split()
        cmd = parts[0]
        params = self._parse_params(parts[1:])

        if cmd in ['G0', 'G1']:
            self._handle_movement(params)
        elif cmd == 'M104': # Set Extruder Temp (No Wait)
            self.target_temp['nozzle'] = params.get('S', 0)
        elif cmd == 'M109': # Set Extruder Temp (Wait)
            self._handle_heating('nozzle', params.get('S', 0))
        elif cmd == 'M140': # Set Bed Temp (No Wait)
            self.target_temp['bed'] = params.get('S', 0)
        elif cmd == 'M190': # Set Bed Temp (Wait)
            self._handle_heating('bed', params.get('S', 0))

    def _parse_params(self, param_list: List[str]) -> Dict[str, float]:
        params = {}
        for p in param_list:
            if not p: continue
            try:
                key = p[0]
                val = float(p[1:])
                params[key] = val
            except ValueError:
                pass
        return params

    def _handle_movement(self, params: Dict[str, float]):
        # Update Feedrate
        if 'F' in params:
            self.feedrate_mm_min = params['F']

        # Calculate Distance
        start_pos = self.current_pos.copy()
        dist_sq = 0.0
        axes_moved = 0
        
        for axis in ['X', 'Y', 'Z']:
            if axis in params:
                delta = params[axis] - start_pos[axis]
                dist_sq += delta ** 2
                self.current_pos[axis] = params[axis]
                axes_moved += 1
        
        distance_mm = math.sqrt(dist_sq)
        
        # Calculate Time
        speed_mm_s = self.feedrate_mm_min / 60.0
        if speed_mm_s <= 0: speed_mm_s = 1.0 # Avoid div zero
        
        move_time_s = distance_mm / speed_mm_s
        self.total_time_s += move_time_s
        
        # Calculate Energy
        # 1. Kinetic (Stepper Power)
        kinetic_j = move_time_s * self.specs['stepper_power_w'] * axes_moved
        
        # 2. Thermal Maintenance (Heaters on)
        # Assume 50% duty cycle to maintain temp (simplified)
        thermal_power_w = 0.0
        if self.target_temp['nozzle'] > self.specs['ambient_temp_c']:
            thermal_power_w += self.specs['nozzle_heater_power_w'] * 0.5
        if self.target_temp['bed'] > self.specs['ambient_temp_c']:
            thermal_power_w += self.specs['bed_heater_power_w'] * 0.5
            
        thermal_j = move_time_s * thermal_power_w
        
        # 3. Extrusion (Melting)
        extrusion_j = 0.0
        if 'E' in params:
            e_delta = params['E'] - self.current_pos['E']
            # Only count positive extrusion
            if e_delta > 0:
                # Volume = Length * Area
                radius = self.specs['filament_diameter_mm'] / 2.0
                area = math.pi * (radius ** 2)
                volume_mm3 = e_delta * area
                mass_g = (volume_mm3 / 1000.0) * self.specs['filament_density_g_cm3']
                
                # Q = mcΔT
                delta_t = self.target_temp['nozzle'] - self.specs['ambient_temp_c']
                extrusion_j = mass_g * self.specs['filament_heat_capacity_j_g_k'] * delta_t
            
            self.current_pos['E'] = params['E']

        self.total_energy_j += (kinetic_j + thermal_j + extrusion_j)

    def _handle_heating(self, heater: str, target_temp: float):
        # Calculate time to heat up
        current = self.current_temp[heater]
        delta_t = target_temp - current
        if delta_t <= 0:
            self.target_temp[heater] = target_temp
            return

        # Estimate heating rate (deg/sec) - Simplified
        rate = 2.0 if heater == 'nozzle' else 0.5
        time_s = delta_t / rate
        
        power_w = self.specs[f'{heater}_heater_power_w']
        energy_j = time_s * power_w
        
        self.total_energy_j += energy_j
        self.total_time_s += time_s
        self.current_temp[heater] = target_temp
        self.target_temp[heater] = target_temp
