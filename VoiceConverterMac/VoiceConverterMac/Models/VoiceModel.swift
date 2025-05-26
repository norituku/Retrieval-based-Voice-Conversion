//
//  VoiceModel.swift
//  VoiceConverterMac
//
//  Voice Model Data Structure
//

import Foundation
import SwiftUI

// MARK: - Voice Model
struct VoiceModel: Identifiable, Hashable {
    let id = UUID()
    let name: String
    let description: String
    let modelPath: String
    let configPath: String
    let sampleRate: Int
    let author: String
    let createdDate: Date
    let fileSize: Int64
    let tags: [String]
    let previewURL: URL?
    
    var formattedFileSize: String {
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        return formatter.string(fromByteCount: fileSize)
    }
    
    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: createdDate)
    }
}

// MARK: - Audio File
struct AudioFile: Identifiable {
    let id = UUID()
    let url: URL
    let duration: TimeInterval
    let sampleRate: Int
    let channels: Int
    
    var fileName: String {
        url.lastPathComponent
    }
    
    var formattedDuration: String {
        let formatter = DateComponentsFormatter()
        formatter.allowedUnits = [.minute, .second]
        formatter.zeroFormattingBehavior = .pad
        return formatter.string(from: duration) ?? "0:00"
    }
}

// MARK: - Conversion Settings
struct ConversionSettings {
    var pitch: Double = 0.0
    var formant: Double = 0.0
    var indexRate: Double = 0.75
    var volumeEnvelope: Double = 0.25
    var protectVoiceless: Double = 0.5
    var hopLength: Int = 128
    var filterRadius: Int = 3
    var resampleRate: Int = 0
    var rmsMixRate: Double = 0.25
    var f0Method: F0Method = .harvest
    
    enum F0Method: String, CaseIterable {
        case harvest = "harvest"
        case crepe = "crepe"
        case rmvpe = "rmvpe"
        case pm = "pm"
        
        var displayName: String {
            switch self {
            case .harvest: return "Harvest (Fast)"
            case .crepe: return "Crepe (High Quality)"
            case .rmvpe: return "RMVPE (Balanced)"
            case .pm: return "PM (Legacy)"
            }
        }
    }
}

// MARK: - Conversion Task
class ConversionTask: ObservableObject, Identifiable {
    let id = UUID()
    let inputFile: AudioFile
    let outputURL: URL
    let model: VoiceModel
    let settings: ConversionSettings
    
    @Published var status: Status = .pending
    @Published var progress: Double = 0.0
    @Published var currentStep: String = ""
    @Published var estimatedTimeRemaining: TimeInterval?
    
    enum Status {
        case pending
        case processing
        case completed
        case failed(Error)
        case cancelled
    }
    
    init(inputFile: AudioFile, outputURL: URL, model: VoiceModel, settings: ConversionSettings) {
        self.inputFile = inputFile
        self.outputURL = outputURL
        self.model = model
        self.settings = settings
    }
}
