import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import math

logger = logging.getLogger(__name__)

class GarminService:
    """Service to parse Garmin TCX files and extract workout data."""

    NAMESPACE = {'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}

    def parse_tcx(self, xml_content: bytes) -> Dict[str, Any]:
        """Parse TCX content and return a dictionary of workout metrics and track points."""
        try:
            root = ET.fromstring(xml_content)
            
            # Find the first Activity
            activity = root.find('.//ns:Activity', self.NAMESPACE)
            if activity is None:
                raise ValueError("No activity found in TCX file")

            sport = activity.get('Sport', 'Other').lower()
            id_tag = activity.find('ns:Id', self.NAMESPACE)
            start_date_str = id_tag.text if id_tag is not None else datetime.now().isoformat()
            
            summary = {
                "name": f"Treino Garmin - {sport.capitalize()}",
                "sport_type": sport,
                "start_date": start_date_str,
                "total_time": 0.0,
                "total_distance": 0.0,
                "avg_hr": None,
                "max_hr": None,
                "calories": 0,
                "track_points": [],
                "laps": []
            }

            hr_values = []
            laps = activity.findall('ns:Lap', self.NAMESPACE)
            
            all_trackpoints = []

            for lap in laps:
                lap_data = {
                    "start_time": lap.get('StartTime'),
                    "total_time": float(lap.find('ns:TotalTimeSeconds', self.NAMESPACE).text or 0),
                    "distance": float(lap.find('ns:DistanceMeters', self.NAMESPACE).text or 0),
                    "max_speed": float(lap.find('ns:MaximumSpeed', self.NAMESPACE).text or 0) if lap.find('ns:MaximumSpeed', self.NAMESPACE) is not None else 0,
                    "calories": int(lap.find('ns:Calories', self.NAMESPACE).text or 0)
                }
                
                summary["total_time"] += lap_data["total_time"]
                summary["total_distance"] += lap_data["distance"]
                summary["calories"] += lap_data["calories"]
                
                # Extract Trackpoints
                track = lap.find('ns:Track', self.NAMESPACE)
                if track is not None:
                    points = track.findall('ns:Trackpoint', self.NAMESPACE)
                    for pt in points:
                        tp = self._parse_trackpoint(pt)
                        if tp:
                            all_trackpoints.append(tp)
                            if tp.get('hr'):
                                hr_values.append(tp['hr'])
                
                summary["laps"].append(lap_data)

            if hr_values:
                summary["avg_hr"] = sum(hr_values) / len(hr_values)
                summary["max_hr"] = max(hr_values)
            
            summary["track_points"] = all_trackpoints
            
            # Set name based on duration/distance if possible
            if summary["total_distance"] > 0:
                dist_km = summary["total_distance"] / 1000
                summary["name"] = f"{sport.capitalize()} de {dist_km:.2f}km"

            return summary

        except Exception as e:
            logger.error(f"Error parsing TCX: {e}")
            raise

    def _parse_trackpoint(self, pt_element: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract data from a single Trackpoint element."""
        try:
            time = pt_element.find('ns:Time', self.NAMESPACE).text
            
            pos = pt_element.find('ns:Position', self.NAMESPACE)
            lat = float(pos.find('ns:LatitudeDegrees', self.NAMESPACE).text) if pos is not None else None
            lng = float(pos.find('ns:LongitudeDegrees', self.NAMESPACE).text) if pos is not None else None
            
            alt = pt_element.find('ns:AltitudeMeters', self.NAMESPACE)
            alt_val = float(alt.text) if alt is not None else None
            
            dist = pt_element.find('ns:DistanceMeters', self.NAMESPACE)
            dist_val = float(dist.text) if dist is not None else None
            
            hr = pt_element.find('.//ns:HeartRateBpm/ns:Value', self.NAMESPACE)
            hr_val = int(hr.text) if hr is not None else None
            
            cad = pt_element.find('ns:Cadence', self.NAMESPACE)
            cad_val = int(cad.text) if cad is not None else None

            return {
                "time": time,
                "lat": lat,
                "lng": lng,
                "alt": alt_val,
                "distance": dist_val,
                "hr": hr_val,
                "cadence": cad_val
            }
        except Exception:
            return None

garmin_service = GarminService()
