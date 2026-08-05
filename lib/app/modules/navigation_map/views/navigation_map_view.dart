import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../routes/app_pages.dart';
import '../../../data/app_colors.dart';
import '../controllers/navigation_map_controller.dart';

class NavigationMapView extends GetView<NavigationMapController> {
  const NavigationMapView({super.key});

  @override
  Widget build(BuildContext context) {
    // Titik koordinat simulasi rute ekspedisi
    const LatLng lokasiDriver = LatLng(-6.2088, 106.8456);
    const LatLng lokasiTujuan = LatLng(-6.2200, 106.8600);

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          // 1. MAP MONITORING UTAMA (FULLSCREEN & DARK THEME)
          FlutterMap(
            options: const MapOptions(
              initialCenter: LatLng(-6.2130, 106.8520), 
              initialZoom: 14.5,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.example.flutter_application_1',
                tileBuilder: (context, tileWidget, tile) {
                  return ColorFiltered(
                    colorFilter: const ColorFilter.matrix([
                      -1.0, 0.0, 0.0, 0.0, 255.0,
                      0.0, -1.0, 0.0, 0.0, 255.0,
                      0.0, 0.0, -1.0, 0.0, 255.0,
                      0.0, 0.0, 0.0, 1.0, 0.0,
                    ]),
                    child: tileWidget,
                  );
                },
              ),
              
              // DRAW RUTE JALAN EKSPEDISI (POLYLINE BERWARNA NEON)
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: const [
                      lokasiDriver,
                      LatLng(-6.2120, 106.8480),
                      LatLng(-6.2150, 106.8530),
                      lokasiTujuan,
                    ],
                    color: AppColors.accentBlue,
                    strokeWidth: 4.5,
                  ),
                ],
              ),

              // MARKER MONITORING TRUK & TUJUAN
              MarkerLayer(
                markers: [
                  // Marker Driver (Icon Truk Logistik)
                  Marker(
                    point: lokasiDriver, 
                    width: 50,
                    height: 50,
                    child: Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.accentBlue, 
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: const Text(
                            "TRUCK-01", 
                            style: TextStyle(color: Colors.black, fontSize: 8, fontWeight: FontWeight.bold),
                          ),
                        ),
                        const Icon(Icons.local_shipping, color: AppColors.accentBlue, size: 30),
                      ],
                    ),
                  ),
                  
                  // Marker Tujuan Ekspedisi (Sudah Diperbaiki Menggunakan child)
                  Marker(
                    point: lokasiTujuan, 
                    width: 40,
                    height: 40,
                    child: const Icon(Icons.location_on, color: AppColors.alertRed, size: 35),
                  ),
                ],
              ),
            ],
          ),

          // 2. TOMBOL KEMBALI KE DASHBOARD CONTROL ROOM
          Positioned(
            top: 50,
            left: 16,
            child: GestureDetector(
              onTap: () => Get.back(),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.cardBg,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white10),
                  boxShadow: [BoxShadow(color: Colors.black54, blurRadius: 8)],
                ),
                child: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 16),
              ),
            ),
          ),

          // 3. TOP MONITORING PANEL (INFO STATUS DRIVER REAL-TIME)
          Positioned(
            top: 50,
            left: 76,
            right: 16,
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.cardBg.withOpacity(0.9), 
                borderRadius: BorderRadius.circular(12), 
                border: Border.all(color: Colors.white.withOpacity(0.08)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.radar, color: AppColors.safeGreen, size: 24),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("FLEET MONITORING ACTIVE", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 0.5)),
                        Obx(() => Text(
                          "Tracking ID: #EXP-9921  |  ETA: ${controller.eta.value}", 
                          style: const TextStyle(color: AppColors.textMuted, fontSize: 11),
                        )),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // 4. NEAREST FUEL STATION FLOATING CHIP
          Positioned(
            top: 220,
            right: 40,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.cardBg, 
                borderRadius: BorderRadius.circular(20), 
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 4)],
              ),
              child: const Row(
                children: [
                  Icon(Icons.local_gas_station, color: Colors.orange, size: 14),
                  SizedBox(width: 4),
                  Text("Nearest Fuel Station", style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
          ),

          // 5. SIDE PANEL (LIVE DRIVER METRICS PANEL)
          Positioned(
            top: 120,
            left: 16,
            child: Container(
              width: 140,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.cardBg.withOpacity(0.9),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white10),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("DRIVER STATUS", style: TextStyle(color: AppColors.textMuted, fontSize: 9, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  _buildMetricRow(Icons.speed, "Speed", "${controller.speed.value} mph"),
                  _buildMetricRow(Icons.local_gas_station, "Fuel", "88%"),
                  _buildMetricRow(Icons.health_and_safety, "Safety", "92%"),
                  const Divider(color: Colors.white10),
                  Row(
                    children: [
                      Container(width: 8, height: 8, decoration: const BoxDecoration(color: AppColors.safeGreen, shape: BoxShape.circle)),
                      const SizedBox(width: 6),
                      const Text("CAM ONLINE", style: TextStyle(color: AppColors.safeGreen, fontSize: 9, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // 6. BOTTOM CONTROL PANEL (ACTION HUB EKSPEDISI)
          Positioned(
            bottom: 20,
            left: 16,
            right: 16,
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: AppColors.cardBg.withOpacity(0.95), borderRadius: BorderRadius.circular(12)),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text("ROUTE: Origin ➔ Port of Oakland", style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                          Text("Cargo Type: Class A Logistics Assets", style: TextStyle(color: AppColors.textMuted, fontSize: 10)),
                        ],
                      ),
                      Icon(Icons.hub, color: AppColors.accentBlue, size: 20),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        icon: const Icon(Icons.analytics, size: 16, color: Colors.white),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1F242C), 
                          minimumSize: const Size(double.infinity, 48), 
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        onPressed: () => Get.toNamed(Routes.DELIVERY_HISTORY),
                        label: const Text("RECORDS", style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        icon: const Icon(Icons.videocam, size: 16, color: Colors.black),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.accentBlue, 
                          minimumSize: const Size(double.infinity, 48), 
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        onPressed: () => Get.toNamed(Routes.DROWSINESS),
                        label: const Text("LIVE AI CAM", style: TextStyle(color: Colors.black, fontSize: 13, fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, color: AppColors.accentBlue, size: 14),
          const SizedBox(width: 6),
          Expanded(child: Text(label, style: const TextStyle(color: Colors.white70, fontSize: 10))),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}