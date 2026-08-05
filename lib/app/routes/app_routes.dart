part of 'app_pages.dart';

abstract class Routes {
  Routes._();
  static const DASHBOARD = _Paths.DASHBOARD;
  static const NAVIGATION_MAP = _Paths.NAVIGATION_MAP;
  static const DROWSINESS = _Paths.DROWSINESS;
  static const DELIVERY_HISTORY = _Paths.DELIVERY_HISTORY;
}

abstract class _Paths {
  _Paths._();
  static const DASHBOARD = '/dashboard';
  static const NAVIGATION_MAP = '/navigation-map';
  static const DROWSINESS = '/drowsiness';
  static const DELIVERY_HISTORY = '/delivery-history';
}