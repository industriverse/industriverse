/**
 * GOOGLE MAPS FRONTEND INTEGRATION - ESSENTIAL GUIDE
 *
 * USAGE FROM PARENT COMPONENT:
 * ======
 *
 * const mapRef = useRef<google.maps.Map | null>(null);
 *
 * <MapView
 *   initialCenter={{ lat: 40.7128, lng: -74.0060 }}
 *   initialZoom={15}
 *   onMapReady={(map) => {
 *     mapRef.current = map; // Store to control map from parent anytime, google map itself is in charge of the re-rendering, not react state.
 * </MapView>
 *
 * ======
 * Available Libraries and Core Features:
 * -------------------------------
 * 📍 MARKER (from `marker` library)
 * - Attaches to map using { map, position }
 * new google.maps.marker.AdvancedMarkerElement({
 *   map,
 *   position: { lat: 37.7749, lng: -122.4194 },
 *   title: "San Francisco",
 * });
 *
 * -------------------------------
 * 🏢 PLACES (from `places` library)
 * - Does not attach directly to map; use data with your map manually.
 * const place = new google.maps.places.Place({ id: PLACE_ID });
 * await place.fetchFields({ fields: ["displayName", "location"] });
 * map.setCenter(place.location);
 * new google.maps.marker.AdvancedMarkerElement({ map, position: place.location });
 *
 * -------------------------------
 * 🧭 GEOCODER (from `geocoding` library)
 * - Standalone service; manually apply results to map.
 * const geocoder = new google.maps.Geocoder();
 * geocoder.geocode({ address: "New York" }, (results, status) => {
 *   if (status === "OK" && results[0]) {
 *     map.setCenter(results[0].geometry.location);
 *     new google.maps.marker.AdvancedMarkerElement({
 *       map,
 *       position: results[0].geometry.location,
 *     });
 *   }
 * });
 *
 * -------------------------------
 * 📐 GEOMETRY (from `geometry` library)
 * - Pure utility functions; not attached to map.
 * const dist = google.maps.geometry.spherical.computeDistanceBetween(p1, p2);
 *
 * -------------------------------
 * 🛣️ ROUTES (from `routes` library)
 * - Combines DirectionsService (standalone) + DirectionsRenderer (map-attached)
 * const directionsService = new google.maps.DirectionsService();
 * const directionsRenderer = new google.maps.DirectionsRenderer({ map });
 * directionsService.route(
 *   { origin, destination, travelMode: "DRIVING" },
 *   (res, status) => status === "OK" && directionsRenderer.setDirections(res)
 * );
 *
 * -------------------------------
 * 🌦️ MAP LAYERS (attach directly to map)
 * - new google.maps.TrafficLayer().setMap(map);
 * - new google.maps.TransitLayer().setMap(map);
 * - new google.maps.BicyclingLayer().setMap(map);
 *
 * -------------------------------
 * ✅ SUMMARY
 * - “map-attached” → AdvancedMarkerElement, DirectionsRenderer, Layers.
 * - “standalone” → Geocoder, DirectionsService, DistanceMatrixService, ElevationService.
 * - “data-only” → Place, Geometry utilities.
 */
import { __awaiter, __generator } from "tslib";
/// <reference types="@types/google.maps" />
import { useEffect, useRef } from "react";
import { usePersistFn } from "@/hooks/usePersistFn";
import { cn } from "@/lib/utils";
var API_KEY = import.meta.env.VITE_FRONTEND_FORGE_API_KEY;
var FORGE_BASE_URL = import.meta.env.VITE_FRONTEND_FORGE_API_URL ||
    "https://forge.butterfly-effect.dev";
var MAPS_PROXY_URL = "".concat(FORGE_BASE_URL, "/v1/maps/proxy");
function loadMapScript() {
    return new Promise(function (resolve) {
        var script = document.createElement("script");
        script.src = "".concat(MAPS_PROXY_URL, "/maps/api/js?key=").concat(API_KEY, "&v=weekly&libraries=marker,places,geocoding,geometry");
        script.async = true;
        script.crossOrigin = "anonymous";
        script.onload = function () {
            resolve(null);
            script.remove(); // Clean up immediately
        };
        script.onerror = function () {
            console.error("Failed to load Google Maps script");
        };
        document.head.appendChild(script);
    });
}
export function MapView(_a) {
    var _this = this;
    var className = _a.className, _b = _a.initialCenter, initialCenter = _b === void 0 ? { lat: 37.7749, lng: -122.4194 } : _b, _c = _a.initialZoom, initialZoom = _c === void 0 ? 12 : _c, onMapReady = _a.onMapReady;
    var mapContainer = useRef(null);
    var map = useRef(null);
    var init = usePersistFn(function () { return __awaiter(_this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, loadMapScript()];
                case 1:
                    _a.sent();
                    if (!mapContainer.current) {
                        console.error("Map container not found");
                        return [2 /*return*/];
                    }
                    map.current = new window.google.maps.Map(mapContainer.current, {
                        zoom: initialZoom,
                        center: initialCenter,
                        mapTypeControl: true,
                        fullscreenControl: true,
                        zoomControl: true,
                        streetViewControl: true,
                        mapId: "DEMO_MAP_ID",
                    });
                    if (onMapReady) {
                        onMapReady(map.current);
                    }
                    return [2 /*return*/];
            }
        });
    }); });
    useEffect(function () {
        init();
    }, [init]);
    return (<div ref={mapContainer} className={cn("w-full h-[500px]", className)}/>);
}
//# sourceMappingURL=Map.jsx.map