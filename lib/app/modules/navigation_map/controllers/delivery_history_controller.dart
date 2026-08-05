import 'package:get/get.dart';

class DeliveryRecord {
  final String route, date, duration, status, safetyScore, tripId;
  DeliveryRecord({required this.tripId, required this.route, required this.date, required this.duration, required this.status, required this.safetyScore});
}

class DeliveryHistoryController extends GetxController {
  final historyRecords = <DeliveryRecord>[
    DeliveryRecord(tripId: "Trip #20240503", route: "Chicago ➔ Denver", date: "[ETA was 4d ago]", duration: "127m", status: "SUCCESSFUL", safetyScore: "94%"),
    DeliveryRecord(tripId: "Trip #20240428", route: "Los Angeles ➔ Seattle", date: "[ETA was 4d ago]", duration: "32m", status: "SUCCESSFUL", safetyScore: "94%"),
  ].obs;
}