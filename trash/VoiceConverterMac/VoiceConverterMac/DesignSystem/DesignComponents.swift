//
//  DesignComponents.swift
//  VoiceConverterMac
//
//  Reusable Dark Mode UI Components
//

import SwiftUI

// MARK: - Custom Button Style
struct DarkModeButtonStyle: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled
    let variant: ButtonVariant
    let size: ButtonSize
    
    enum ButtonVariant {
        case primary
        case secondary
        case tertiary
        case destructive
        case ghost
    }
    
    enum ButtonSize {
        case small
        case medium
        case large
        
        var horizontalPadding: CGFloat {
            switch self {
            case .small: return DesignTokens.Spacing.sm
            case .medium: return DesignTokens.Spacing.md
            case .large: return DesignTokens.Spacing.lg
            }
        }
        
        var verticalPadding: CGFloat {
            switch self {
            case .small: return DesignTokens.Spacing.xxs
            case .medium: return DesignTokens.Spacing.xs
            case .large: return DesignTokens.Spacing.sm
            }
        }
        
        var font: Font {
            switch self {
            case .small: return DesignTokens.Typography.caption1
            case .medium: return DesignTokens.Typography.body
            case .large: return DesignTokens.Typography.bodyBold
            }
        }
    }
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(size.font)
            .foregroundColor(foregroundColor(for: variant, isPressed: configuration.isPressed))
            .padding(.horizontal, size.horizontalPadding)
            .padding(.vertical, size.verticalPadding)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                    .fill(backgroundColor(for: variant, isPressed: configuration.isPressed))
            )
            .overlay(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                    .strokeBorder(borderColor(for: variant), lineWidth: variant == .secondary ? 1 : 0)
            )
            .scaleEffect(configuration.isPressed ? 0.97 : 1.0)
            .animation(DesignTokens.Animation.defaultSpring, value: configuration.isPressed)
            .opacity(isEnabled ? 1.0 : 0.5)
    }
    
    private func foregroundColor(for variant: ButtonVariant, isPressed: Bool) -> Color {
        switch variant {
        case .primary:
            return .white
        case .secondary:
            return DesignTokens.Colors.textPrimary
        case .tertiary, .ghost:
            return DesignTokens.Colors.accentPrimary
        case .destructive:
            return .white
        }
    }
    
    private func backgroundColor(for variant: ButtonVariant, isPressed: Bool) -> Color {
        let baseColor: Color
        switch variant {
        case .primary:
            baseColor = DesignTokens.Colors.accentPrimary
        case .secondary:
            baseColor = DesignTokens.Colors.backgroundTertiary
        case .tertiary, .ghost:
            baseColor = .clear
        case .destructive:
            baseColor = DesignTokens.Colors.error
        }
        
        if isPressed {
            return variant == .ghost || variant == .tertiary ? 
                DesignTokens.Colors.hoverOverlay : baseColor.opacity(0.8)
        }
        return baseColor
    }
    
    private func borderColor(for variant: ButtonVariant) -> Color {
        switch variant {
        case .secondary:
            return DesignTokens.Colors.borderSubtle
        default:
            return .clear
        }
    }
}


// MARK: - Custom TextField Style
struct DarkModeTextFieldStyle: TextFieldStyle {
    @FocusState private var isFocused: Bool
    let icon: String?
    
    func _body(configuration: TextField<Self._Label>) -> some View {
        HStack(spacing: DesignTokens.Spacing.xs) {
            if let icon = icon {
                Image(systemName: icon)
                    .foregroundColor(DesignTokens.Colors.textSecondary)
                    .font(.system(size: 14))
            }
            
            configuration
                .textFieldStyle(.plain)
                .font(DesignTokens.Typography.body)
                .foregroundColor(DesignTokens.Colors.textPrimary)
        }
        .padding(DesignTokens.Spacing.sm)
        .background(
            RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                .fill(DesignTokens.Colors.backgroundSecondary)
        )
        .overlay(
            RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                .strokeBorder(
                    isFocused ? DesignTokens.Colors.focusRing : DesignTokens.Colors.borderSubtle,
                    lineWidth: isFocused ? 2 : 1
                )
        )
        .focused($isFocused)
        .animation(DesignTokens.Animation.smooth, value: isFocused)
    }
}

// MARK: - Card Component
struct DarkModeCard<Content: View>: View {
    let content: Content
    var padding: CGFloat = DesignTokens.Spacing.lg
    var backgroundColor: Color = DesignTokens.Colors.surfaceCard
    
    init(padding: CGFloat = DesignTokens.Spacing.lg,
         backgroundColor: Color = DesignTokens.Colors.surfaceCard,
         @ViewBuilder content: () -> Content) {
        self.padding = padding
        self.backgroundColor = backgroundColor
        self.content = content()
    }
    
    var body: some View {
        content
            .padding(padding)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.large)
                    .fill(backgroundColor)
            )
            .overlay(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.large)
                    .strokeBorder(DesignTokens.Colors.borderSubtle, lineWidth: 1)
            )
            .shadow(color: .black.opacity(0.2), radius: 8, x: 0, y: 2)
    }
}

// MARK: - Progress Bar
struct DarkModeProgressBar: View {
    let progress: Double
    let height: CGFloat
    let showPercentage: Bool
    
    init(progress: Double, height: CGFloat = 8, showPercentage: Bool = false) {
        self.progress = max(0, min(1, progress))
        self.height = height
        self.showPercentage = showPercentage
    }
    
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                // Background
                RoundedRectangle(cornerRadius: height / 2)
                    .fill(DesignTokens.Colors.backgroundTertiary)
                    .frame(height: height)
                
                // Progress
                RoundedRectangle(cornerRadius: height / 2)
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [
                                DesignTokens.Colors.accentPrimary,
                                DesignTokens.Colors.accentSecondary
                            ]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: geometry.size.width * progress, height: height)
                    .animation(DesignTokens.Animation.smooth, value: progress)
                
                if showPercentage {
                    Text("\(Int(progress * 100))%")
                        .font(DesignTokens.Typography.caption1)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                        .frame(maxWidth: .infinity)
                }
            }
        }
        .frame(height: height)
    }
}

// MARK: - Icon Button
struct IconButton: View {
    let icon: String
    let action: () -> Void
    let size: CGFloat
    let isSelected: Bool
    
    init(icon: String, size: CGFloat = 24, isSelected: Bool = false, action: @escaping () -> Void) {
        self.icon = icon
        self.size = size
        self.isSelected = isSelected
        self.action = action
    }
    
    @State private var isHovered = false
    
    var body: some View {
        Button(action: action) {
            Image(systemName: icon)
                .font(.system(size: size * 0.7))
                .foregroundColor(isSelected ? DesignTokens.Colors.accentPrimary : DesignTokens.Colors.textSecondary)
                .frame(width: size, height: size)
                .background(
                    Circle()
                        .fill(isHovered || isSelected ? 
                              DesignTokens.Colors.hoverOverlay : 
                              Color.clear)
                )
        }
        .buttonStyle(PlainButtonStyle())
        .onHover { hovering in
            isHovered = hovering
        }
    }
}

// MARK: - Status Badge
struct StatusBadge: View {
    enum Status {
        case success, warning, error, info, processing
        
        var color: Color {
            switch self {
            case .success: return DesignTokens.Colors.success
            case .warning: return DesignTokens.Colors.warning
            case .error: return DesignTokens.Colors.error
            case .info: return DesignTokens.Colors.info
            case .processing: return DesignTokens.Colors.accentPrimary
            }
        }
        
        var icon: String {
            switch self {
            case .success: return "checkmark.circle.fill"
            case .warning: return "exclamationmark.triangle.fill"
            case .error: return "xmark.circle.fill"
            case .info: return "info.circle.fill"
            case .processing: return "arrow.triangle.2.circlepath"
            }
        }
    }
    
    let status: Status
    let text: String
    
    @State private var isAnimating = false
    
    var body: some View {
        HStack(spacing: DesignTokens.Spacing.xs) {
            Image(systemName: status.icon)
                .foregroundColor(status.color)
                .font(.system(size: 14))
                .rotationEffect(.degrees(status == .processing && isAnimating ? 360 : 0))
                .animation(
                    status == .processing ? 
                    Animation.linear(duration: 1).repeatForever(autoreverses: false) : 
                    .default,
                    value: isAnimating
                )
            
            Text(text)
                .font(DesignTokens.Typography.caption1)
                .foregroundColor(DesignTokens.Colors.textPrimary)
        }
        .padding(.horizontal, DesignTokens.Spacing.sm)
        .padding(.vertical, DesignTokens.Spacing.xxs)
        .background(
            RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.small)
                .fill(status.color.opacity(0.2))
        )
        .onAppear {
            if status == .processing {
                isAnimating = true
            }
        }
    }
}

// MARK: - Divider
struct DarkModeDivider: View {
    let orientation: Axis
    
    var body: some View {
        Rectangle()
            .fill(DesignTokens.Colors.divider)
            .frame(
                width: orientation == .horizontal ? nil : 1,
                height: orientation == .vertical ? nil : 1
            )
    }
}
