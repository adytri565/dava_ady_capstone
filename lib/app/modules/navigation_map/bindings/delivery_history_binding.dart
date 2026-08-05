import 'package:get/get.dart';
import '../controllers/delivery_history_controller.dart';

class DeliveryHistoryBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<DeliveryHistoryController>(() => DeliveryHistoryController());
  }
}