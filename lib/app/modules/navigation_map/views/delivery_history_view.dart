import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../../data/app_colors.dart';
import '../controllers/delivery_history_controller.dart';

class DeliveryHistoryView extends GetView<DeliveryHistoryController> {
  const DeliveryHistoryView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: AppColors.background, elevation: 0,
        title: const Text("Delivery History", style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        centerTitle: true,
        leading: IconButton(icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white, size: 18), onPressed: () => Get.back()),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8), child: Text("COMPLETED DELIVERIES", style: TextStyle(color: AppColors.textMuted, fontSize: 11, fontWeight: FontWeight.bold))),
          Expanded(
            child: Obx(() {
              return ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: controller.historyRecords.length,
                itemBuilder: (context, index) {
                  final item = controller.historyRecords[index];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 14), padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(color: AppColors.cardBg, borderRadius: BorderRadius.circular(16), border: Border.all(color: Colors.white.withOpacity(0.04))),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(item.tripId, style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
                            Container(padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2), decoration: BoxDecoration(color: AppColors.safeGreen.withOpacity(0.1), borderRadius: BorderRadius.circular(4)), child: Text(item.status, style: const TextStyle(color: AppColors.safeGreen, fontSize: 8, fontWeight: FontWeight.bold)))
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(item.route, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold)),
                        Text(item.date, style: const TextStyle(color: Colors.white30, fontSize: 11)),
                        const Divider(color: Colors.white10, height: 24),
                        Row(
                          children: [
                            Expanded(
                              child: Column(
                                children: [
                                  _buildRowDetail(Icons.swap_calls_rounded, "Distance"),
                                  _buildRowDetail(Icons.access_time, "Total time: ${item.duration}"),
                                  _buildRowDetail(Icons.gpp_good_outlined, "Driving Safety: ${item.safetyScore}"),
                                  _buildRowDetail(Icons.check_circle_outline_rounded, "Delivery confirmation"),
                                ],
                              ),
                            ),
                            Container(width: 60, height: 60, decoration: BoxDecoration(color: Colors.blueGrey.shade900, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.map_outlined, color: AppColors.accentBlue, size: 24))
                          ],
                        )
                      ],
                    ),
                  );
                },
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _buildRowDetail(IconData icon, String text) {
    return Padding(padding: const EdgeInsets.symmetric(vertical: 2), child: Row(children: [Icon(icon, color: AppColors.safeGreen, size: 13), const SizedBox(width: 6), Text(text, style: const TextStyle(color: Colors.white70, fontSize: 11))]));
  }
}