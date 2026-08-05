import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:http/http.dart' as http;
import '../../../data/app_colors.dart';
import '../controllers/drowsiness_controller.dart';

class DrowsinessView extends GetView<DrowsinessController> {
  const DrowsinessView({super.key});

  // 🟢 FUNGSI CUSTOM STREAM: Memecah data MJPEG Stream + Ekstraksi Metadata Header
  Stream<Uint8List> _mjpegStream(String url) async* {
    final client = http.Client();
    final request = http.Request('GET', Uri.parse(url));
    
    try {
      final response = await client.send(request);
      final stream = response.stream;
      
      List<int> chunks = [];
      
      await for (final chunk in stream) {
        chunks.addAll(chunk);
        
        while (true) {
          int startIndex = -1;
          for (int i = 0; i < chunks.length - 1; i++) {
            if (chunks[i] == 0xFF && chunks[i + 1] == 0xD8) {
              startIndex = i;
              break;
            }
          }
          
          if (startIndex == -1) break;
          
          int endIndex = -1;
          for (int i = startIndex; i < chunks.length - 1; i++) {
            if (chunks[i] == 0xFF && chunks[i + 1] == 0xD9) {
              endIndex = i + 2;
              break;
            }
          }
          
          if (endIndex == -1) break;

          // 🌟 PERBAIKAN: Baca teks header sebelum frame gambar untuk mengambil data AI
          try {
            final headerText = String.fromCharCodes(chunks.sublist(0, startIndex));
            
            final statusMatch = RegExp(r'X-Status:\s*([^\r\n]+)').firstMatch(headerText);
            final earMatch = RegExp(r'X-EAR:\s*([^\r\n]+)').firstMatch(headerText);
            final blinkMatch = RegExp(r'X-Blink:\s*([^\r\n]+)').firstMatch(headerText);
            final poseMatch = RegExp(r'X-Pose:\s*([^\r\n]+)').firstMatch(headerText);

            if (statusMatch != null && earMatch != null && blinkMatch != null && poseMatch != null) {
              // Kirim data ke fungsi updateMetrics di controller Anda
              controller.updateMetrics(
                status: statusMatch.group(1)!,
                currentEar: double.parse(earMatch.group(1)!),
                currentBlinkRate: int.parse(blinkMatch.group(1)!),
                pose: poseMatch.group(1)!,
              );
            }
          } catch (_) {
            // Abaikan jika chunk awal belum terbaca sempurna
          }
          
          // Potong satu frame gambar utuh dan lempar ke UI
          final frameData = chunks.sublist(startIndex, endIndex);
          yield Uint8List.fromList(frameData);
          
          // Hapus frame yang sudah diproses dari memori cache buffer
          chunks = chunks.sublist(endIndex);
        }
      }
    } catch (e) {
      client.close();
      throw Exception("Gagal terhubung ke Flask AI server: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Obx(() {
        if (controller.isDrowsy.value) return _buildEmergencyAlertScreen();
        return _buildLiveCameraScreen();
      }),
    );
  }

  Widget _buildLiveCameraScreen() {
    return Stack(
      children: [
        // 1. REAL-TIME AI CAM STREAM (Menggunakan StreamBuilder Kustom)
        SizedBox(
          width: double.infinity,
          height: double.infinity,
          child: StreamBuilder<Uint8List>(
            stream: _mjpegStream(controller.flaskUrl),
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.videocam_off, color: AppColors.alertRed, size: 40),
                      const SizedBox(height: 12),
                      Text(
                        "CONNECTION FAILED\nURL: ${controller.flaskUrl}",
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.white54, fontSize: 11),
                      ),
                    ],
                  ),
                );
              }
              
              if (!snapshot.hasData) {
                return const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(AppColors.safeGreen)),
                      SizedBox(height: 16),
                      Text("INITIALIZING DSM CAMERA...", style: TextStyle(color: Colors.white54, fontSize: 12)),
                    ],
                  ),
                );
              }

              return Image.memory(
                snapshot.data!,
                gaplessPlayback: true, 
                fit: BoxFit.cover,
              );
            },
          ),
        ),
        
        Container(color: Colors.black.withOpacity(0.2)), 
        
        // 2. DYNAMIC FACE BOUNDING BOX
        Center(
          child: Obx(() {
            final isWarning = controller.aiStatus.value == "MENGANTUK" || controller.aiStatus.value == "KRITIS";
            final boxColor = isWarning ? AppColors.alertRed : AppColors.safeGreen;
            
            return Container(
              width: 220, 
              height: 220,
              decoration: BoxDecoration(
                border: Border.all(color: boxColor, width: 2), 
                borderRadius: BorderRadius.circular(16),
              ),
              child: Stack(
                children: [
                  Positioned(
                    top: 6, 
                    left: 8, 
                    child: Text(
                      isWarning ? "WARNING DETECTED" : "FACE TRACKING ACTIVE", 
                      style: TextStyle(color: boxColor, fontSize: 8, fontWeight: FontWeight.bold, letterSpacing: 0.5),
                    ),
                  ),
                ],
              ),
            );
          }),
        ),

        // 3. TOP MONITORING PANEL
        Positioned(
          top: 50, 
          left: 16, 
          right: 16,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.cardBg.withOpacity(0.85), 
              borderRadius: BorderRadius.circular(16), 
              border: Border.all(color: Colors.white.withOpacity(0.05)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text("AI DROWSINESS MONITORING:", style: TextStyle(color: AppColors.textMuted, fontSize: 11, fontWeight: FontWeight.bold)),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2), 
                      decoration: BoxDecoration(
                        color: AppColors.safeGreen.withOpacity(0.2), 
                        borderRadius: BorderRadius.circular(4),
                      ), 
                      child: const Text("LIVE", style: TextStyle(color: AppColors.safeGreen, fontSize: 8, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween, 
                  children: [
                    const Text("Eye Aspect Ratio (EAR):", style: TextStyle(color: Colors.white70, fontSize: 13)), 
                    Obx(() => Text(
                      controller.ear.value.toStringAsFixed(2), 
                      style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                    )),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween, 
                  children: [
                    const Text("Blink Rate:", style: TextStyle(color: Colors.white70, fontSize: 13)), 
                    Obx(() => Text(
                      "${controller.blinkRate.value}/min", 
                      style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                    )),
                  ],
                ),
                const Divider(color: Colors.white10, height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween, 
                  children: [
                    const Text("SYSTEM STATUS:", style: TextStyle(color: AppColors.textMuted, fontSize: 12)), 
                    Obx(() {
                      final status = controller.aiStatus.value.toUpperCase();
                      final isNormal = status == "FOCUSED" || status == "NORMAL";
                      return Text(
                        status, 
                        style: TextStyle(
                          color: isNormal ? AppColors.safeGreen : AppColors.alertRed, 
                          fontSize: 12, 
                          fontWeight: FontWeight.bold,
                        ),
                      );
                    }),
                  ],
                ),
              ],
            ),
          ),
        ),

        // BACK BUTTON
        Positioned(
          top: 55,
          left: 24,
          child: IconButton(
            icon: const Icon(Icons.arrow_back_ios, color: Colors.white, size: 16),
            onPressed: () => Get.back(),
          ),
        ),

        // 4. BOTTOM HUD CONTROLLER
        Positioned(
          bottom: 40, 
          left: 0, 
          right: 0,
          child: Column(
            children: [
              const Text("CURRENT METRIC LOG:", style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
              Obx(() => Text(
                "POSE: ${controller.headPose.value}", 
                style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
              )),
              const SizedBox(height: 10),
              GestureDetector(
                onLongPress: () => controller.toggleDrowsyStatus(),
                child: Obx(() {
                  final isWarning = controller.aiStatus.value == "MENGANTUK" || controller.aiStatus.value == "KRITIS";
                  return Container(
                    height: 64, 
                    width: 64, 
                    decoration: BoxDecoration(
                      color: isWarning ? AppColors.alertRed : AppColors.safeGreen, 
                      shape: BoxShape.circle, 
                      boxShadow: [
                        BoxShadow(
                          color: (isWarning ? AppColors.alertRed : AppColors.safeGreen).withOpacity(0.4), 
                          blurRadius: 15, 
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: const Icon(Icons.radar, color: Colors.black, size: 28),
                  );
                }),
              ),
              const SizedBox(height: 6),
              const Text("Hold radar button to force simulate emergency", style: TextStyle(color: Colors.white24, fontSize: 10)),
            ],
          ),
        )
      ],
    );
  }

  Widget _buildEmergencyAlertScreen() {
    return Container(
      width: double.infinity, 
      padding: const EdgeInsets.symmetric(horizontal: 24),
      decoration: const BoxDecoration(
        color: Color(0xFF500505), 
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 60),
          const Text("EMERGENCY", style: TextStyle(color: Colors.white70, fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 2)),
          const Spacer(),
          Container(
            width: 160, 
            height: 160, 
            decoration: BoxDecoration(border: Border.all(color: AppColors.alertRed, width: 2), borderRadius: BorderRadius.circular(16)), 
            child: const Center(child: Icon(Icons.warning_amber_rounded, color: AppColors.alertRed, size: 50)),
          ),
          const SizedBox(height: 30),
          const Text("WARNING:\nDROWSINESS DETECTED!", textAlign: TextAlign.center, style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          const Text("Emergency Alert Sent to Operations Center", style: TextStyle(color: Colors.white54, fontSize: 11)),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(14), 
            decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(12)), 
            width: double.infinity,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Recommendations:", style: TextStyle(color: Colors.white70, fontSize: 11, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                _buildBulletItem("1. PULL OVER SAFELY."),
                _buildBulletItem("2. USE NEAREST REST AREA (ETA 5m)."),
                _buildBulletItem("3. Wait for confirmation"),
              ],
            ),
          ),
          const Spacer(),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.alertRed, 
              minimumSize: const Size(double.infinity, 50), 
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
            ),
            onPressed: () => controller.acknowledgeAndRestart(),
            child: const Text(
              "ACKNOWLEDGE & RESTART ROUTE", 
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
            ),
          ),
          const SizedBox(height: 10),
          TextButton(
            onPressed: () {}, 
            child: const Text("CALL OPERATIONS", style: TextStyle(color: Colors.white60, fontSize: 12, decoration: TextDecoration.underline)),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildBulletItem(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2), 
      child: Text(
        text, 
        style: const TextStyle(
          color: Colors.white70, 
          fontSize: 11, 
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}