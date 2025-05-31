//
//  SettingsView.swift
//  VoiceConverterMac
//
//  Settings Interface
//

import SwiftUI

struct SettingsView: View {
    @Environment(\.dismiss) var dismiss
    @State private var selectedTab = SettingsTab.general
    
    enum SettingsTab: String, CaseIterable {
        case general = "General"
        case audio = "Audio"
        case advanced = "Advanced"
        case about = "About"
        
        var icon: String {
            switch self {
            case .general: return "gear"
            case .audio: return "waveform"
            case .advanced: return "slider.horizontal.3"
            case .about: return "info.circle"
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Settings")
                    .font(DesignTokens.Typography.title2)
                    .foregroundColor(DesignTokens.Colors.textPrimary)
                
                Spacer()
                
                Button(action: { dismiss() }) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                }
                .buttonStyle(PlainButtonStyle())
            }
            .padding(DesignTokens.Spacing.lg)
            
            DarkModeDivider(orientation: .horizontal)
            
            // Tab View
            TabView(selection: $selectedTab) {
                GeneralSettingsView()
                    .tabItem {
                        Label(SettingsTab.general.rawValue, 
                              systemImage: SettingsTab.general.icon)
                    }
                    .tag(SettingsTab.general)
                
                AudioSettingsView()
                    .tabItem {
                        Label(SettingsTab.audio.rawValue, 
                              systemImage: SettingsTab.audio.icon)
                    }
                    .tag(SettingsTab.audio)
                
                AdvancedSettingsView()
                    .tabItem {
                        Label(SettingsTab.advanced.rawValue, 
                              systemImage: SettingsTab.advanced.icon)
                    }
                    .tag(SettingsTab.advanced)
                
                AboutView()
                    .tabItem {
                        Label(SettingsTab.about.rawValue, 
                              systemImage: SettingsTab.about.icon)
                    }
                    .tag(SettingsTab.about)
            }
            .padding(DesignTokens.Spacing.lg)
        }
        .frame(width: 700, height: 500)
        .background(DesignTokens.Colors.backgroundPrimary)
    }
}

// MARK: - General Settings
struct GeneralSettingsView: View {
    @AppStorage("outputDirectory") private var outputDirectory = ""
    @AppStorage("autoPlayAfterConversion") private var autoPlay = false
    @AppStorage("showNotifications") private var showNotifications = true
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DesignTokens.Spacing.xl) {
                SettingsSection(title: "Output") {
                    // Output Directory
                    VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                        Text("Output Directory")
                            .font(DesignTokens.Typography.caption1)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                        
                        HStack {
                            Text(outputDirectory.isEmpty ? "Default" : outputDirectory)
                                .font(DesignTokens.Typography.body)
                                .foregroundColor(DesignTokens.Colors.textPrimary)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(DesignTokens.Spacing.sm)
                                .background(
                                    RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                                        .fill(DesignTokens.Colors.backgroundSecondary)
                                )
                            
                            Button("Choose...") {
                                // File picker
                            }
                            .buttonStyle(DarkModeButtonStyle(variant: .secondary, size: .small))
                        }
                    }
                    
                    Toggle("Auto-play after conversion", isOn: $autoPlay)
                        .toggleStyle(SwitchToggleStyle(tint: DesignTokens.Colors.accentPrimary))
                }
                
                SettingsSection(title: "Notifications") {
                    Toggle("Show notifications", isOn: $showNotifications)
                        .toggleStyle(SwitchToggleStyle(tint: DesignTokens.Colors.accentPrimary))
                }
            }
            .padding(DesignTokens.Spacing.lg)
        }
    }
}

// MARK: - Audio Settings
struct AudioSettingsView: View {
    @AppStorage("defaultSampleRate") private var sampleRate = 48000
    @AppStorage("defaultBitDepth") private var bitDepth = 16
    @AppStorage("normalizeAudio") private var normalizeAudio = true
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DesignTokens.Spacing.xl) {
                SettingsSection(title: "Default Audio Settings") {
                    // Sample Rate
                    VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                        Text("Sample Rate")
                            .font(DesignTokens.Typography.caption1)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                        
                        Picker("", selection: $sampleRate) {
                            Text("44.1 kHz").tag(44100)
                            Text("48 kHz").tag(48000)
                            Text("96 kHz").tag(96000)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    // Bit Depth
                    VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                        Text("Bit Depth")
                            .font(DesignTokens.Typography.caption1)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                        
                        Picker("", selection: $bitDepth) {
                            Text("16-bit").tag(16)
                            Text("24-bit").tag(24)
                            Text("32-bit").tag(32)
                        }
                        .pickerStyle(SegmentedPickerStyle())
                    }
                    
                    Toggle("Normalize audio levels", isOn: $normalizeAudio)
                        .toggleStyle(SwitchToggleStyle(tint: DesignTokens.Colors.accentPrimary))
                }
            }
            .padding(DesignTokens.Spacing.lg)
        }
    }
}

// MARK: - Advanced Settings
struct AdvancedSettingsView: View {
    @AppStorage("gpuAcceleration") private var gpuAcceleration = true
    @AppStorage("maxThreads") private var maxThreads = 4
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: DesignTokens.Spacing.xl) {
                SettingsSection(title: "Performance") {
                    Toggle("GPU Acceleration", isOn: $gpuAcceleration)
                        .toggleStyle(SwitchToggleStyle(tint: DesignTokens.Colors.accentPrimary))
                    
                    VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                        Text("Max Threads")
                            .font(DesignTokens.Typography.caption1)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                        
                        HStack {
                            Slider(value: .init(get: { Double(maxThreads) }, 
                                              set: { maxThreads = Int($0) }), 
                                   in: 1...8, 
                                   step: 1)
                            
                            Text("\(maxThreads)")
                                .font(DesignTokens.Typography.body)
                                .foregroundColor(DesignTokens.Colors.textPrimary)
                                .frame(width: 30)
                        }
                    }
                }
            }
            .padding(DesignTokens.Spacing.lg)
        }
    }
}

// MARK: - About View
struct AboutView: View {
    var body: some View {
        ScrollView {
            VStack(spacing: DesignTokens.Spacing.xl) {
                // App Icon and Info
                VStack(spacing: DesignTokens.Spacing.md) {
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 80))
                        .foregroundStyle(
                            LinearGradient(
                                colors: [
                                    DesignTokens.Colors.accentPrimary,
                                    DesignTokens.Colors.accentSecondary
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                    
                    Text("Voice Converter")
                        .font(DesignTokens.Typography.title1)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                    
                    Text("Version 1.0.0")
                        .font(DesignTokens.Typography.body)
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                }
                
                DarkModeDivider(orientation: .horizontal)
                    .frame(width: 200)
                
                // Credits
                VStack(spacing: DesignTokens.Spacing.sm) {
                    Text("Built with RVC technology")
                        .font(DesignTokens.Typography.body)
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                    
                    Link("Visit GitHub Repository", 
                         destination: URL(string: "https://github.com")!)
                        .font(DesignTokens.Typography.body)
                        .foregroundColor(DesignTokens.Colors.accentPrimary)
                }
                
                Spacer(minLength: DesignTokens.Spacing.xl)
                
                Text("© 2024 Voice Converter. All rights reserved.")
                    .font(DesignTokens.Typography.caption1)
                    .foregroundColor(DesignTokens.Colors.textTertiary)
            }
            .padding(DesignTokens.Spacing.lg)
            .frame(maxWidth: .infinity)
        }
    }
}

// MARK: - Settings Section
struct SettingsSection<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: DesignTokens.Spacing.md) {
            Text(title)
                .font(DesignTokens.Typography.headline)
                .foregroundColor(DesignTokens.Colors.textPrimary)
            
            VStack(alignment: .leading, spacing: DesignTokens.Spacing.md) {
                content
            }
            .padding(DesignTokens.Spacing.md)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                    .fill(DesignTokens.Colors.backgroundSecondary)
            )
        }
    }
}

// MARK: - Preview
struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
            .preferredColorScheme(.dark)
    }
}