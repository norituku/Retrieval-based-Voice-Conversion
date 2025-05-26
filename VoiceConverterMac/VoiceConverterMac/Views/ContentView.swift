//
//  ContentView.swift
//  VoiceConverterMac
//
//  Main Content View with Dark Mode Design
//

import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = VoiceConverterViewModel()
    @State private var selectedSidebarItem = SidebarItem.convert
    @State private var showingSettings = false
    
    enum SidebarItem: String, CaseIterable {
        case convert = "Convert"
        case models = "Models"
        case history = "History"
        
        var icon: String {
            switch self {
            case .convert: return "waveform"
            case .models: return "cube.box.fill"
            case .history: return "clock.fill"
            }
        }
    }
    
    var body: some View {
        NavigationSplitView {
            // Sidebar
            sidebarView
                .navigationSplitViewColumnWidth(
                    min: 240,
                    ideal: DesignTokens.Layout.sidebarWidth,
                    max: 400
                )
        } detail: {
            // Main Content
            ZStack {
                DesignTokens.Colors.backgroundPrimary
                    .ignoresSafeArea()
                
                switch selectedSidebarItem {
                case .convert:
                    ConversionView()
                case .models:
                    ModelsView()
                case .history:
                    HistoryView()
                }
            }
        }
        .environmentObject(viewModel)
        .frame(
            minWidth: DesignTokens.Layout.minWindowWidth,
            minHeight: DesignTokens.Layout.minWindowHeight
        )
    }
    
    private var sidebarView: some View {
        VStack(spacing: 0) {
            // App Header
            VStack(spacing: DesignTokens.Spacing.xs) {
                HStack {
                    Image(systemName: "waveform.circle.fill")
                        .font(.system(size: 36))
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
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("Voice Converter")
                            .font(DesignTokens.Typography.title2)
                            .foregroundColor(DesignTokens.Colors.textPrimary)
                        
                        Text("Professional Audio Processing")
                            .font(DesignTokens.Typography.caption1)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                    }
                    
                    Spacer()
                }
                .padding(DesignTokens.Spacing.lg)
            }
            
            DarkModeDivider(orientation: .horizontal)
            
            // Navigation Items
            VStack(spacing: DesignTokens.Spacing.xs) {
                ForEach(SidebarItem.allCases, id: \.self) { item in
                    SidebarItemView(
                        item: item,
                        isSelected: selectedSidebarItem == item
                    ) {
                        selectedSidebarItem = item
                    }
                }
            }
            .padding(DesignTokens.Spacing.md)
            
            Spacer()
            
            // Bottom Actions
            VStack(spacing: DesignTokens.Spacing.sm) {
                DarkModeDivider(orientation: .horizontal)
                
                HStack {
                    Button(action: { showingSettings = true }) {
                        Label("Settings", systemImage: "gear")
                            .font(DesignTokens.Typography.body)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .padding(DesignTokens.Spacing.md)
                    
                    Spacer()
                }
            }
        }
        .background(DesignTokens.Colors.surfaceSidebar)
        .sheet(isPresented: $showingSettings) {
            SettingsView()
        }
    }
}

// MARK: - Sidebar Item View
struct SidebarItemView: View {
    let item: ContentView.SidebarItem
    let isSelected: Bool
    let action: () -> Void
    
    @State private var isHovered = false
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: DesignTokens.Spacing.sm) {
                Image(systemName: item.icon)
                    .font(.system(size: 16))
                    .foregroundColor(
                        isSelected ? 
                        DesignTokens.Colors.accentPrimary : 
                        DesignTokens.Colors.textSecondary
                    )
                    .frame(width: 24)
                
                Text(item.rawValue)
                    .font(DesignTokens.Typography.body)
                    .foregroundColor(
                        isSelected ? 
                        DesignTokens.Colors.textPrimary : 
                        DesignTokens.Colors.textSecondary
                    )
                
                Spacer()
            }
            .padding(.horizontal, DesignTokens.Spacing.sm)
            .padding(.vertical, DesignTokens.Spacing.xs)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                    .fill(
                        isSelected ? 
                        DesignTokens.Colors.selectionBackground : 
                        (isHovered ? DesignTokens.Colors.hoverOverlay : Color.clear)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
        .onHover { hovering in
            withAnimation(DesignTokens.Animation.smooth) {
                isHovered = hovering
            }
        }
    }
}

// MARK: - Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .preferredColorScheme(.dark)
    }
}
