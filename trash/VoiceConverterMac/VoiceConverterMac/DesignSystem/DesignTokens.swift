//
//  DesignTokens.swift
//  VoiceConverterMac
//
//  Dark Mode Design System Tokens
//

import SwiftUI

// MARK: - Design Tokens
enum DesignTokens {
    // MARK: Base Colors
    enum Colors {
        // Background hierarchy - Optimized for Voice Converter App
        static let backgroundPrimary = Color(hex: "0F0F0F")    // Pure black background
        static let backgroundSecondary = Color(hex: "1A1A1A")   // Panels and cards
        static let backgroundTertiary = Color(hex: "252525")    // Elevated surfaces
        static let backgroundElevated = Color(hex: "2F2F2F")    // Highest elevation
        
        // Surface colors for components
        static let surfaceCard = Color(hex: "1F1F21")
        static let surfaceOverlay = Color(hex: "2A2A2C")
        static let surfacePopover = Color(hex: "252527")
        static let surfaceSidebar = Color(hex: "151517")
        
        // Text colors with optimal contrast for dark mode
        static let textPrimary = Color(hex: "FFFFFF").opacity(0.90)
        static let textSecondary = Color(hex: "FFFFFF").opacity(0.65)
        static let textTertiary = Color(hex: "FFFFFF").opacity(0.45)
        static let textDisabled = Color(hex: "FFFFFF").opacity(0.25)
        
        // Brand colors - Music/Audio themed
        static let accentPrimary = Color(hex: "4C8BF5")     // Bright blue
        static let accentSecondary = Color(hex: "7B61FF")   // Purple
        static let accentTertiary = Color(hex: "FF6B6B")    // Coral red
        static let accentQuaternary = Color(hex: "4ECDC4")  // Teal
        
        // System semantic colors
        static let success = Color(hex: "4ADE80")
        static let warning = Color(hex: "FBBF24")
        static let error = Color(hex: "F87171")
        static let info = Color(hex: "60A5FA")
        
        // Interactive states
        static let hoverOverlay = Color.white.opacity(0.08)
        static let pressedOverlay = Color.white.opacity(0.12)
        static let focusRing = Color(hex: "4C8BF5").opacity(0.8)
        static let selectionBackground = Color(hex: "4C8BF5").opacity(0.3)
        
        // Dividers and borders
        static let divider = Color(hex: "FFFFFF").opacity(0.10)
        static let borderSubtle = Color(hex: "FFFFFF").opacity(0.15)
        static let borderStrong = Color(hex: "FFFFFF").opacity(0.25)
        
        // Special colors for audio visualization
        static let waveformPrimary = Color(hex: "4C8BF5")
        static let waveformSecondary = Color(hex: "7B61FF")
        static let spectrumGradientStart = Color(hex: "4C8BF5")
        static let spectrumGradientEnd = Color(hex: "7B61FF")
    }
    
    // MARK: Typography - SF Pro for macOS
    enum Typography {
        static let largeTitle = Font.system(size: 34, weight: .regular, design: .default)
        static let title1 = Font.system(size: 28, weight: .regular, design: .default)
        static let title2 = Font.system(size: 22, weight: .regular, design: .default)
        static let title3 = Font.system(size: 20, weight: .regular, design: .default)
        static let headline = Font.system(size: 17, weight: .semibold, design: .default)
        static let body = Font.system(size: 15, weight: .regular, design: .default)
        static let bodyBold = Font.system(size: 15, weight: .semibold, design: .default)
        static let callout = Font.system(size: 14, weight: .regular, design: .default)
        static let subheadline = Font.system(size: 13, weight: .regular, design: .default)
        static let footnote = Font.system(size: 12, weight: .regular, design: .default)
        static let caption1 = Font.system(size: 11, weight: .regular, design: .default)
        static let caption2 = Font.system(size: 11, weight: .regular, design: .default)
        
        // Monospaced for technical info
        static let mono = Font.system(size: 13, design: .monospaced)
        static let monoSmall = Font.system(size: 11, design: .monospaced)
    }
    
    // MARK: Spacing - 4pt grid system
    enum Spacing {
        static let xxxs: CGFloat = 2
        static let xxs: CGFloat = 4
        static let xs: CGFloat = 8
        static let sm: CGFloat = 12
        static let md: CGFloat = 16
        static let lg: CGFloat = 20
        static let xl: CGFloat = 24
        static let xxl: CGFloat = 32
        static let xxxl: CGFloat = 40
        static let xxxxl: CGFloat = 48
    }
    
    // MARK: Corner Radius
    enum CornerRadius {
        static let tiny: CGFloat = 2
        static let small: CGFloat = 4
        static let medium: CGFloat = 8
        static let large: CGFloat = 12
        static let extraLarge: CGFloat = 16
        static let round: CGFloat = 9999
    }
    
    // MARK: Animation
    enum Animation {
        static let instant: Double = 0.0
        static let microDuration: Double = 0.1
        static let shortDuration: Double = 0.2
        static let mediumDuration: Double = 0.35
        static let longDuration: Double = 0.5
        static let extraLongDuration: Double = 0.8
        
        static let defaultSpring = SwiftUI.Animation.spring(response: 0.5, dampingFraction: 0.825)
        static let bouncy = SwiftUI.Animation.spring(response: 0.4, dampingFraction: 0.75)
        static let smooth = SwiftUI.Animation.easeOut(duration: shortDuration)
        static let smoothIn = SwiftUI.Animation.easeIn(duration: shortDuration)
        static let linear = SwiftUI.Animation.linear(duration: mediumDuration)
    }
    
    // MARK: Layout
    enum Layout {
        static let sidebarWidth: CGFloat = 320
        static let minWindowWidth: CGFloat = 1200
        static let minWindowHeight: CGFloat = 800
        static let toolbarHeight: CGFloat = 52
        static let playerHeight: CGFloat = 120
    }
}

// MARK: - Color Extension
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
