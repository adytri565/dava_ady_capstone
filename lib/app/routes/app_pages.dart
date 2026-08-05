import 'package:get/get.dart';

import '../modules/navigation_map/bindings/dashboard_binding.dart';
import '../modules/navigation_map/views/dashboard_view.dart';
import '../modules/navigation_map/bindings/navigation_map_binding.dart';
import '../modules/navigation_map/views/navigation_map_view.dart';
import '../modules/navigation_map/bindings/drowsiness_binding.dart';
import '../modules/navigation_map/views/drowsiness_view.dart';
import '../modules/navigation_map/bindings/delivery_history_binding.dart';
import '../modules/navigation_map/views/delivery_history_view.dart';

part 'app_routes.dart';

class AppPages {
  AppPages._();

  static const INITIAL = Routes.DASHBOARD;

  static final routes = [
    GetPage(name: Routes.DASHBOARD, page: () => const DashboardView(), binding: DashboardBinding()),
    GetPage(name: Routes.NAVIGATION_MAP, page: () => const NavigationMapView(), binding: NavigationMapBinding()),
    GetPage(name: Routes.DROWSINESS, page: () => const DrowsinessView(), binding: DrowsinessBinding()),
    GetPage(name: Routes.DELIVERY_HISTORY, page: () => const DeliveryHistoryView(), binding: DeliveryHistoryBinding()),
  ];
}