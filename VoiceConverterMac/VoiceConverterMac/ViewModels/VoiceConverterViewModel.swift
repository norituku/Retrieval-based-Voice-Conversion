//
//  VoiceConverterViewModel.swift
//  VoiceConverterMac
//
//  Main ViewModel for Voice Converter App
//

import Foundation
import SwiftUI
import Combine
import AVFoundation

@MainActor
class VoiceConverterViewModel: ObservableObject {
    // MARK: - Published Properties
    @Published var availableModels: [VoiceModel] = []
    @Published var selectedModel: VoiceModel?
    @Published var inputFile: AudioFile?
    @Published var conversionSettings = ConversionSettings()
    @Published var conversionTasks: [ConversionTask] = []
    @Published var isProcessing = false
    @Published var errorMessage: String?
    
    // Audio playback
    @Published var isPlaying = false
    @Published var currentPlaybackTime: TimeInterval = 0
    @Published var playbackDuration: TimeInterval = 0
    
    // MARK: - Private Properties
    private var audioPlayer: AVAudioPlayer?
    private var playbackTimer: Timer?
    private let pythonScriptPath: String
    private let modelDirectory: URL
    
    // MARK: - Initialization
    init() {
        // Set up paths
        if let bundlePath = Bundle.main.resourcePath {
            self.pythonScriptPath = "\(bundlePath)/rvc_cli.py"
            self.modelDirectory = URL(fileURLWithPath: "\(bundlePath)/model_dir")
        } else {
            self.pythonScriptPath = ""
            self.modelDirectory = URL(fileURLWithPath: "")
        }
        
        loadAvailableModels()
    }
    
    // MARK: - Model Management
    func loadAvailableModels() {
        // Mock data for now - replace with actual model loading
        availableModels = [
            VoiceModel(
                name: "Soprano Voice",
                description: "High-quality soprano voice model trained on classical vocals",
                modelPath: "soprano_v2.pth",
                configPath: "soprano_v2.json",
                sampleRate: 48000,
                author: "VoiceAI Lab",
                createdDate: Date().addingTimeInterval(-86400 * 7),
                fileSize: 536870912,
                tags: ["Female", "Classical", "High Quality"],
                previewURL: nil
            ),
            VoiceModel(
                name: "Deep Bass",
                description: "Rich bass voice perfect for narration and podcasts",
                modelPath: "bass_enhanced.pth",
                configPath: "bass_enhanced.json",
                sampleRate: 44100,
                author: "AudioCraft",
                createdDate: Date().addingTimeInterval(-86400 * 14),
                fileSize: 429496729,
                tags: ["Male", "Narration", "Deep"],
                previewURL: nil
            ),
            VoiceModel(
                name: "Natural Speaking",
                description: "Versatile model for natural conversation and dialogue",
                modelPath: "natural_v3.pth",
                configPath: "natural_v3.json",
                sampleRate: 48000,
                author: "OpenVoice",
                createdDate: Date().addingTimeInterval(-86400 * 3),
                fileSize: 644245094,
                tags: ["Neutral", "Conversational", "Versatile"],
                previewURL: nil
            )
        ]
        
        // Select first model by default
        if selectedModel == nil && !availableModels.isEmpty {
            selectedModel = availableModels[0]
        }
    }
    
    // MARK: - File Management
    func selectInputFile(url: URL) {
        // Create AudioFile from URL
        let asset = AVAsset(url: url)
        let duration = CMTimeGetSeconds(asset.duration)
        
        inputFile = AudioFile(
            url: url,
            duration: duration,
            sampleRate: 48000, // Will be determined from actual file
            channels: 2
        )
    }
    
    func clearInputFile() {
        inputFile = nil
        stopPlayback()
    }
    
    // MARK: - Conversion
    func startConversion() {
        guard let input = inputFile,
              let model = selectedModel else { return }
        
        let outputURL = generateOutputURL(for: input.url)
        let task = ConversionTask(
            inputFile: input,
            outputURL: outputURL,
            model: model,
            settings: conversionSettings
        )
        
        conversionTasks.append(task)
        isProcessing = true
        
        // Start conversion process
        Task {
            await performConversion(task: task)
        }
    }
    
    private func generateOutputURL(for inputURL: URL) -> URL {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, 
                                                     in: .userDomainMask)[0]
        let outputFolder = documentsPath.appendingPathComponent("VoiceConverter_Output")
        
        // Create output directory if needed
        try? FileManager.default.createDirectory(at: outputFolder, 
                                                withIntermediateDirectories: true)
        
        let timestamp = DateFormatter.localizedString(from: Date(), 
                                                     dateStyle: .none, 
                                                     timeStyle: .medium)
            .replacingOccurrences(of: ":", with: "-")
        
        let outputName = "\(inputURL.deletingPathExtension().lastPathComponent)_converted_\(timestamp).wav"
        return outputFolder.appendingPathComponent(outputName)
    }
    
    private func performConversion(task: ConversionTask) async {
        // Update task status
        await MainActor.run {
            task.status = .processing
            task.currentStep = "Initializing..."
        }
        
        // Simulate conversion progress
        for i in 0...10 {
            try? await Task.sleep(nanoseconds: 500_000_000) // 0.5 seconds
            
            await MainActor.run {
                task.progress = Double(i) / 10.0
                
                switch i {
                case 0...2:
                    task.currentStep = "Loading model..."
                case 3...5:
                    task.currentStep = "Processing audio..."
                case 6...8:
                    task.currentStep = "Applying voice conversion..."
                case 9...10:
                    task.currentStep = "Finalizing output..."
                default:
                    break
                }
            }
        }
        
        // Complete
        await MainActor.run {
            task.status = .completed
            self.isProcessing = false
        }
    }
    
    // MARK: - Audio Playback
    func playAudio(url: URL) {
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.prepareToPlay()
            audioPlayer?.play()
            isPlaying = true
            
            playbackDuration = audioPlayer?.duration ?? 0
            
            // Start playback timer
            playbackTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
                self.updatePlaybackTime()
            }
        } catch {
            errorMessage = "Failed to play audio: \(error.localizedDescription)"
        }
    }
    
    func stopPlayback() {
        audioPlayer?.stop()
        audioPlayer = nil
        isPlaying = false
        currentPlaybackTime = 0
        playbackTimer?.invalidate()
        playbackTimer = nil
    }
    
    func togglePlayback(url: URL) {
        if isPlaying {
            audioPlayer?.pause()
            isPlaying = false
        } else if audioPlayer != nil {
            audioPlayer?.play()
            isPlaying = true
        } else {
            playAudio(url: url)
        }
    }
    
    private func updatePlaybackTime() {
        currentPlaybackTime = audioPlayer?.currentTime ?? 0
        
        if !isPlaying || currentPlaybackTime >= playbackDuration {
            stopPlayback()
        }
    }
    
    // MARK: - Settings
    func resetSettings() {
        conversionSettings = ConversionSettings()
    }
}
