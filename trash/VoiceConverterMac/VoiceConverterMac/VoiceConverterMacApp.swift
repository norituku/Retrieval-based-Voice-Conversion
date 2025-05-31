//
//  VoiceConverterMacApp.swift
//  VoiceConverterMac
//
//  Main App Entry Point
//

import SwiftUI

@main
struct VoiceConverterMacApp: App {
    // Force dark mode
    init() {
        // Set appearance to dark
        NSApp.appearance = NSAppearance(named: .darkAqua)
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
        }
        .windowStyle(.hiddenTitleBar)
        .windowToolbarStyle(.unified(showsTitle: false))
        .commands {
            // Custom menu commands
            CommandGroup(replacing: .appInfo) {
                Button("About Voice Converter") {
                    showAboutWindow()
                }
            }
            
            CommandGroup(after: .appSettings) {
                Button("Preferences...") {
                    showPreferences()
                }
                .keyboardShortcut(",", modifiers: .command)
            }
        }
    }
    
    private func showAboutWindow() {
        let aboutView = AboutWindow()
        let hostingController = NSHostingController(rootView: aboutView)
        
        let window = NSWindow(contentViewController: hostingController)
        window.title = "About Voice Converter"
        window.styleMask = [.titled, .closable]
        window.isReleasedWhenClosed = false
        window.center()
        window.makeKeyAndOrderFront(nil)
    }
    
    private func showPreferences() {
        let settingsView = SettingsView()
        let hostingController = NSHostingController(rootView: settingsView)
        
        let window = NSWindow(contentViewController: hostingController)
        window.title = "Preferences"
        window.styleMask = [.titled, .closable]
        window.isReleasedWhenClosed = false
        window.center()
        window.makeKeyAndOrderFront(nil)
    }
}

// MARK: - About Window
struct AboutWindow: View {
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: DesignTokens.Spacing.xl) {
            // App Icon
            Image(systemName: "waveform.circle.fill")
                .font(.system(size: 100))
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
            
            // App Info
            VStack(spacing: DesignTokens.Spacing.sm) {
                Text("Voice Converter")
                    .font(DesignTokens.Typography.title1)
                    .foregroundColor(DesignTokens.Colors.textPrimary)
                
                Text("Version 1.0.0")
                    .font(DesignTokens.Typography.body)
                    .foregroundColor(DesignTokens.Colors.textSecondary)
                
                Text("Professional Audio Voice Conversion")
                    .font(DesignTokens.Typography.caption1)
                    .foregroundColor(DesignTokens.Colors.textTertiary)
            }
            
            // System Info
            VStack(spacing: DesignTokens.Spacing.xs) {
                Text("Powered by RVC Technology")
                    .font(DesignTokens.Typography.caption1)
                    .foregroundColor(DesignTokens.Colors.textSecondary)
                
                Text("© 2024 Voice Converter. All rights reserved.")
                    .font(DesignTokens.Typography.caption2)
                    .foregroundColor(DesignTokens.Colors.textTertiary)
            }
            
            // Close Button
            Button("Done") {
                dismiss()
            }
            .buttonStyle(DarkModeButtonStyle(variant: .primary, size: .medium))
            .padding(.top)
        }
        .padding(DesignTokens.Spacing.xxxl)
        .frame(width: 400)
        .background(DesignTokens.Colors.backgroundPrimary)
    }
}

// MARK: - Window Extensions
extension NSWindow {
    func enableDarkMode() {
        self.appearance = NSAppearance(named: .darkAqua)
        self.backgroundColor = NSColor(DesignTokens.Colors.backgroundPrimary)
        self.isOpaque = false
        self.titlebarAppearsTransparent = true
    }
}