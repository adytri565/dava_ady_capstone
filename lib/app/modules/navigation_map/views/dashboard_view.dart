import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../routes/app_pages.dart';
// Jika masih butuh AppColors untuk warna lain, bisa dipertahankan. 
// Di sini saya gunakan warna bawaan Flutter untuk menjamin tema terang.
import '../controllers/dashboard_controller.dart';

class DashboardView extends GetView<DashboardController> {
  const DashboardView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // Latar belakang abu-abu muda sesuai permintaan
      backgroundColor: Colors.grey.shade100,
      
      body: SafeArea(
        // Membuat seluruh halaman bisa di-scroll dari atas ke bawah
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ==========================
              // HEADER: WELCOME & PROFILE AVATAR MAP
              // ==========================
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "WELCOME,",
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                        Obx(() => Text(
                          controller.driverName.value.toUpperCase(),
                          style: const TextStyle(
                            color: Colors.black87, // Teks gelap untuk light theme
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        )),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.05),
                          blurRadius: 10,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Icon(
                      Icons.map,
                      color: Colors.blue.shade700,
                      size: 20,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // ==========================
              // KARTU UTAMA: CURRENT DELIVERY
              // ==========================
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white, // Latar kartu putih
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.blue.withOpacity(0.1),
                      blurRadius: 15,
                      offset: const Offset(0, 5),
                    ),
                  ],
                  border: Border.all(
                    color: Colors.blue.shade100,
                    width: 1.5,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          "Current Delivery",
                          style: TextStyle(
                            color: Colors.black87,
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.green.shade100,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            "ACTIVE",
                            style: TextStyle(
                              color: Colors.green.shade800,
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        )
                      ],
                    ),
                    const SizedBox(height: 20),
                    Text(
                      "DESTINATION:",
                      style: TextStyle(
                        color: Colors.blue.shade700,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Obx(() => Text(
                      controller.destination.value,
                      style: TextStyle(
                        color: Colors.blue.shade800,
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    )),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: Colors.blue.shade700,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade300,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 4),
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade300,
                            shape: BoxShape.circle,
                          ),
                        ),
                      ],
                    )
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // ==========================
              // GRID INFORMASI BARIS 1
              // ==========================
              Row(
                children: [
                  Expanded(
                    child: _buildInfoCard(
                      "Next Stop",
                      Obx(() => Text(
                        controller.etaNextStop.value,
                        style: const TextStyle(
                          color: Colors.black87,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      )),
                      subtitle: "ETA: 1h 45m",
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildInfoCard(
                      "Route Progress",
                      Obx(() => Text(
                        "${controller.routeProgress.value}%",
                        style: const TextStyle(
                          color: Colors.black87,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      )),
                      progressValue: controller.routeProgress.value / 100,
                      progressColor: Colors.blue.shade600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // ==========================
              // GRID INFORMASI BARIS 2
              // ==========================
              Row(
                children: [
                  Expanded(
                    child: _buildInfoCard(
                      "Driver Safety Score",
                      Obx(() => Text(
                        "${controller.safetyScore.value}%",
                        style: const TextStyle(
                          color: Colors.black87,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      )),
                      progressValue: controller.safetyScore.value / 100,
                      progressColor: Colors.green,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildInfoCard(
                      "Vehicle Status",
                      Obx(() => Text(
                        "Fuel: ${controller.fuelStatus.value}%",
                        style: const TextStyle(
                          color: Colors.black87,
                          fontSize: 15,
                          fontWeight: FontWeight.bold,
                        ),
                      )),
                      progressValue: controller.fuelStatus.value / 100,
                      progressColor: Colors.blue.shade600,
                    ),
                  ),
                ],
              ),
              
              // Memberikan jarak yang cukup sebelum navigation bar
              const SizedBox(height: 40),

              // ==========================
              // NAVIGATION BAR FIX
              // ==========================
              Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildNavItem(
                      Icons.map,
                      "MAP",
                      isActive: true,
                      onTap: () => Get.toNamed(Routes.NAVIGATION_MAP),
                    ),
                    _buildNavItem(
                      Icons.history,
                      "HISTORY",
                      isActive: false,
                      onTap: () => Get.toNamed(Routes.DELIVERY_HISTORY),
                    ),
                    _buildNavItem(
                      Icons.person,
                      "PROFILE",
                      isActive: false,
                      onTap: () {},
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper Widget yang disesuaikan untuk Light Theme
  Widget _buildInfoCard(
    String title,
    Widget valueWidget, {
    String? subtitle,
    double? progressValue,
    Color? progressColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      height: 95,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 8,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            title,
            style: TextStyle(
              color: Colors.grey.shade600,
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
          if (subtitle != null)
            Text(
              subtitle,
              style: TextStyle(color: Colors.grey.shade500, fontSize: 10),
            ),
          valueWidget,
          if (progressValue != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: progressValue,
                backgroundColor: Colors.grey.shade200,
                color: progressColor ?? Colors.blue,
                minHeight: 4,
              ),
            )
        ],
      ),
    );
  }

  // Helper Widget Navigasi yang disesuaikan untuk Light Theme
  Widget _buildNavItem(
    IconData icon,
    String label, {
    required bool isActive,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? Colors.blue.shade700 : Colors.grey.shade400,
            size: 20,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              color: isActive ? Colors.blue.shade700 : Colors.grey.shade400,
              fontSize: 9,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}