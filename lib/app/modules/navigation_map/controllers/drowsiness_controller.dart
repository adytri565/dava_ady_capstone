import 'package:get/get.dart';

class DrowsinessController extends GetxController {
  // 🌟 Sesuaikan dengan IP Flask Anda saat ini
  final String flaskUrl = "http://192.168.18.37:5000/video_feed";

  // State Reaktif untuk Obx di View
  var isDrowsy = false.obs;
  var ear = 0.28.obs;
  var blinkRate = 0.obs;
  var aiStatus = "FOCUSED".obs;
  var headPose = "NORMAL".obs;

  // Fungsi untuk memperbarui data indikator berdasarkan header HTTP dari Flask
  void updateMetrics({
    required String status,
    required double currentEar,
    required int currentBlinkRate,
    required String pose,
  }) {
    aiStatus.value = status;
    ear.value = currentEar;
    blinkRate.value = currentBlinkRate;
    headPose.value = pose;

    // 🧠 Otomatis memicu Layar Kritis/Mengantuk tanpa perlu di-hold manual
    if (status == "MENGANTUK" || status == "KRITIS") {
      isDrowsy.value = true;
    }
  }

  void acknowledgeAndRestart() {
    isDrowsy.value = false;
    aiStatus.value = "FOCUSED";
  }
  
  void toggleDrowsyStatus() {
    isDrowsy.value = !isDrowsy.value;
  }
}