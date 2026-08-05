// lib/app/modules/navigation_map/controllers/dashboard_controller.dart
import 'package:get/get.dart';

class DashboardController extends GetxController {
  var driverName = "".obs;
  var destination = "Port of Oakland".obs;
  var etaNextStop = "1h 45m".obs;
  var routeProgress = 68.obs;
  var safetyScore = 92.obs;
  var fuelStatus = 88.obs;

  @override
  void onInit() {
    super.onInit();
    _loadLoggedInUser();
  }

  void _loadLoggedInUser() {
    // Inisialisasi awal string kosong (Non-nullable)
    String sessionName = ""; 

    // PERBAIKAN: Hapus kondisi pengecekan '!= null' karena operand tidak mungkin null
    if (sessionName.isNotEmpty) {
      driverName.value = sessionName;
    } else {
      driverName.value = "Driver";
    }
  }
}