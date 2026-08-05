import 'package:get/get.dart';
import '../controllers/drowsiness_controller.dart';

class DrowsinessBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<DrowsinessController>(() => DrowsinessController());
  }
}