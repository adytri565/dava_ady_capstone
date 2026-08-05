// lib/app/modules/navigation_map/controllers/navigation_map_controller.dart
import 'package:get/get.dart';

class NavigationMapController extends GetxController {
  var eta = "18 Mins".obs;
  var speed = "45".obs;
  
  // 🌟 KUNCI: Ubah ke IP Laptop sesuai dengan log Flask Anda tadi!
  // Tambahkan endpoint /video_feed di akhirnya.
  final String flaskUrl = "http://10.0.2.2:5000/video_feed";
}