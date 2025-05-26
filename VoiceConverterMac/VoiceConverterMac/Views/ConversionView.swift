//
//  ConversionView.swift
//  VoiceConverterMac
//
//  Main Conversion Interface
//

import SwiftUI
import UniformTypeIdentifiers

struct ConversionView: View {
    @EnvironmentObject var viewModel: VoiceConverterViewModel
    @State private var isDragging = false
    @State private var showingFilePicker = false
    
    var body: some View {
        ScrollView {
            VStack(spacing: DesignTokens.Spacing.xl) {
                // Header
                headerSection
                
                // Input Section
                inputSection
                
                // Model Selection
                if viewModel.inputFile != nil {
                    modelSelectionSection
                    
                    // Settings
                    settingsSection
                    
                    // Conversion Button
                    conversionButton
                }
                
                // Active Conversions
                if !viewModel.conversionTasks.isEmpty {
                    activeConversionsSection
                }
            }
            .padding(DesignTokens.Spacing.xxl)
        }
    }
    
    // MARK: - Header Section
    private var headerSection: some View {
        VStack(alignment: .leading, spacing: DesignTokens.Spacing.sm) {
            Text("Voice Conversion")
                .font(DesignTokens.Typography.largeTitle)
                .foregroundColor(DesignTokens.Colors.textPrimary)
            
            Text("Transform audio files using AI-powered voice models")
                .font(DesignTokens.Typography.body)
                .foregroundColor(DesignTokens.Colors.textSecondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
    
    // MARK: - Input Section
    private var inputSection: some View {
        DarkModeCard {
            VStack(spacing: DesignTokens.Spacing.lg) {
                // Drag & Drop Area
                ZStack {
                    RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.large)
                        .strokeBorder(
                            style: StrokeStyle(
                                lineWidth: 2,
                                dash: [8, 4]
                            )
                        )
                        .foregroundColor(
                            isDragging ? 
                            DesignTokens.Colors.accentPrimary : 
                            DesignTokens.Colors.borderSubtle
                        )
                        .background(
                            RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.large)
                                .fill(
                                    isDragging ? 
                                    DesignTokens.Colors.accentPrimary.opacity(0.1) : 
                                    DesignTokens.Colors.backgroundSecondary
                                )
                        )
                        .frame(height: 200)
                    
                    if let inputFile = viewModel.inputFile {
                        // File Info
                        VStack(spacing: DesignTokens.Spacing.md) {
                            Image(systemName: "waveform")
                                .font(.system(size: 48))
                                .foregroundColor(DesignTokens.Colors.accentPrimary)
                            
                            Text(inputFile.fileName)
                                .font(DesignTokens.Typography.headline)
                                .foregroundColor(DesignTokens.Colors.textPrimary)
                            
                            HStack(spacing: DesignTokens.Spacing.lg) {
                                Label(inputFile.formattedDuration, systemImage: "clock")
                                Label("\(inputFile.sampleRate) Hz", systemImage: "waveform.path")
                            }
                            .font(DesignTokens.Typography.caption1)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                            
                            HStack(spacing: DesignTokens.Spacing.md) {
                                Button("Play") {
                                    viewModel.togglePlayback(url: inputFile.url)
                                }
                                .buttonStyle(DarkModeButtonStyle(variant: .secondary, size: .small))
                                
                                Button("Remove") {
                                    viewModel.clearInputFile()
                                }
                                .buttonStyle(DarkModeButtonStyle(variant: .ghost, size: .small))
                            }
                        }
                    } else {
                        // Empty State
                        VStack(spacing: DesignTokens.Spacing.md) {
                            Image(systemName: "arrow.down.doc")
                                .font(.system(size: 48))
                                .foregroundColor(DesignTokens.Colors.textTertiary)
                            
                            Text("Drop audio file here")
                                .font(DesignTokens.Typography.headline)
                                .foregroundColor(DesignTokens.Colors.textSecondary)
                            
                            Text("or")
                                .font(DesignTokens.Typography.caption1)
                                .foregroundColor(DesignTokens.Colors.textTertiary)
                            
                            Button("Browse Files") {
                                showingFilePicker = true
                            }
                            .buttonStyle(DarkModeButtonStyle(variant: .primary, size: .medium))
                        }
                    }
                }
                .onDrop(of: [.audio], isTargeted: $isDragging) { providers in
                    handleDrop(providers: providers)
                }
            }
        }
        .fileImporter(
            isPresented: $showingFilePicker,
            allowedContentTypes: [.audio],
            allowsMultipleSelection: false
        ) { result in
            handleFileSelection(result: result)
        }
    }
replacingUnspecifiedDimensions().width,
            subviews: subviews,
            spacing: spacing
        )
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(
            in: bounds.width,
            subviews: subviews,
            spacing: spacing
        )
        
        for row in result.rows {
            for item in row.items {
                let x = bounds.minX + item.x
                let y = bounds.minY + row.y
                
                subviews[item.index].place(
                    at: CGPoint(x: x, y: y),
                    anchor: .topLeading,
                    proposal: ProposedViewSize(item.size)
                )
            }
        }
    }
    
    struct FlowResult {
        var rows: [Row] = []
        var size: CGSize = .zero
        
        struct Row {
            var items: [Item] = []
            var y: CGFloat = 0
            var height: CGFloat = 0
        }
        
        struct Item {
            var index: Int
            var x: CGFloat
            var size: CGSize
        }
        
        init(in width: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var currentRow = Row()
            var x: CGFloat = 0
            var y: CGFloat = 0
            var maxWidth: CGFloat = 0
            
            for (index, subview) in subviews.enumerated() {
                let size = subview.sizeThatFits(.unspecified)
                
                if x + size.width > width && !currentRow.items.isEmpty {
                    currentRow.y = y
                    rows.append(currentRow)
                    y += currentRow.height + spacing
                    currentRow = Row()
                    x = 0
                }
                
                currentRow.items.append(Item(index: index, x: x, size: size))
                currentRow.height = max(currentRow.height, size.height)
                x += size.width + spacing
                maxWidth = max(maxWidth, x - spacing)
            }
            
            if !currentRow.items.isEmpty {
                currentRow.y = y
                rows.append(currentRow)
                y += currentRow.height
            }
            
            self.size = CGSize(width: maxWidth, height: y)
        }
    }
}

// MARK: - Preview
struct ConversionView_Previews: PreviewProvider {
    static var previews: some View {
        ConversionView()
            .environmentObject(VoiceConverterViewModel())
            .preferredColorScheme(.dark)
            .frame(width: 1200, height: 800)
    }
}