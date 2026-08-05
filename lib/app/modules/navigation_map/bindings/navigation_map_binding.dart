import 'package:get/get.dart';
import '../controllers/navigation_map_controller.dart';

class NavigationMapBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<NavigationMapController>(() => NavigationMapController());
  }
}