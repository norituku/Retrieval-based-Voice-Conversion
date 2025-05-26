//
//  ModelsView.swift
//  VoiceConverterMac
//
//  Model Management Interface
//

import SwiftUI

struct ModelsView: View {
    @EnvironmentObject var viewModel: VoiceConverterViewModel
    @State private var searchText = ""
    @State private var selectedFilter = ModelFilter.all
    @State private var showingImport = false
    
    enum ModelFilter: String, CaseIterable {
        case all = "All Models"
        case female = "Female"
        case male = "Male"
        case neutral = "Neutral"
        
        var icon: String {
            switch self {
            case .all: return "square.grid.2x2"
            case .female: return "person.fill"
            case .male: return "person.fill"
            case .neutral: return "person.2.fill"
            }
        }
    }
    
    var filteredModels: [VoiceModel] {
        viewModel.availableModels.filter { model in
            let matchesSearch = searchText.isEmpty || 
                model.name.localizedCaseInsensitiveContains(searchText) ||
                model.description.localizedCaseInsensitiveContains(searchText)
            
            let matchesFilter = selectedFilter == .all ||
                model.tags.contains(selectedFilter.rawValue.capitalized)
            
            return matchesSearch && matchesFilter
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerSection
            
            DarkModeDivider(orientation: .horizontal)
            
            // Content
            if filteredModels.isEmpty {
                emptyState
            } else {
                modelGrid
            }
        }
    }
    
    private var headerSection: some View {
        VStack(spacing: DesignTokens.Spacing.lg) {
            // Title and Actions
            HStack {
                VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                    Text("Voice Models")
                        .font(DesignTokens.Typography.largeTitle)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                    
                    Text("\(viewModel.availableModels.count) models available")
                        .font(DesignTokens.Typography.body)
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                }
                
                Spacer()
                
                Button(action: { showingImport = true }) {
                    Label("Import Model", systemImage: "plus.circle.fill")
                }
                .buttonStyle(DarkModeButtonStyle(variant: .primary, size: .medium))
            }
            
            // Search and Filters
            HStack(spacing: DesignTokens.Spacing.md) {
                // Search Field
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                    
                    TextField("Search models...", text: $searchText)
                        .textFieldStyle(.plain)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                }
                .padding(DesignTokens.Spacing.sm)
                .background(
                    RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                        .fill(DesignTokens.Colors.backgroundSecondary)
                )
                .frame(maxWidth: 300)
                
                // Filter Buttons
                HStack(spacing: DesignTokens.Spacing.xs) {
                    ForEach(ModelFilter.allCases, id: \.self) { filter in
                        FilterChip(
                            title: filter.rawValue,
                            icon: filter.icon,
                            isSelected: selectedFilter == filter
                        ) {
                            selectedFilter = filter
                        }
                    }
                }
                
                Spacer()
            }
        }
        .padding(DesignTokens.Spacing.xxl)
    }
    
    private var modelGrid: some View {
        ScrollView {
            LazyVGrid(
                columns: [
                    GridItem(.adaptive(minimum: 300), spacing: DesignTokens.Spacing.lg)
                ],
                spacing: DesignTokens.Spacing.lg
            ) {
                ForEach(filteredModels) { model in
                    ModelDetailCard(model: model)
                }
            }
            .padding(DesignTokens.Spacing.xxl)
        }
    }
    
    private var emptyState: some View {
        VStack(spacing: DesignTokens.Spacing.lg) {
            Image(systemName: "cube.box")
                .font(.system(size: 64))
                .foregroundColor(DesignTokens.Colors.textTertiary)
            
            Text("No models found")
                .font(DesignTokens.Typography.headline)
                .foregroundColor(DesignTokens.Colors.textSecondary)
            
            Text("Try adjusting your search or filters")
                .font(DesignTokens.Typography.body)
                .foregroundColor(DesignTokens.Colors.textTertiary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Filter Chip
struct FilterChip: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: DesignTokens.Spacing.xxs) {
                Image(systemName: icon)
                    .font(.system(size: 12))
                
                Text(title)
                    .font(DesignTokens.Typography.caption1)
            }
            .foregroundColor(
                isSelected ? 
                DesignTokens.Colors.accentPrimary : 
                DesignTokens.Colors.textSecondary
            )
            .padding(.horizontal, DesignTokens.Spacing.sm)
            .padding(.vertical, DesignTokens.Spacing.xxs)
            .background(
                Capsule()
                    .fill(
                        isSelected ? 
                        DesignTokens.Colors.accentPrimary.opacity(0.2) : 
                        DesignTokens.Colors.backgroundTertiary
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Model Detail Card
struct ModelDetailCard: View {
    let model: VoiceModel
    @State private var isHovered = false
    @State private var showingDetails = false
    
    var body: some View {
        DarkModeCard(
            padding: 0,
            backgroundColor: isHovered ? 
                DesignTokens.Colors.surfaceCard : 
                DesignTokens.Colors.backgroundSecondary
        ) {
            VStack(spacing: 0) {
                // Header with gradient
                ZStack {
                    LinearGradient(
                        colors: [
                            DesignTokens.Colors.accentPrimary.opacity(0.3),
                            DesignTokens.Colors.accentSecondary.opacity(0.3)
                        ],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    
                    HStack {
                        Image(systemName: "waveform.circle.fill")
                            .font(.system(size: 32))
                            .foregroundColor(.white)
                        
                        Spacer()
                        
                        VStack(alignment: .trailing) {
                            Text(model.formattedFileSize)
                                .font(DesignTokens.Typography.caption1)
                                .foregroundColor(.white.opacity(0.8))
                            
                            Text("\(model.sampleRate) Hz")
                                .font(DesignTokens.Typography.caption2)
                                .foregroundColor(.white.opacity(0.6))
                        }
                    }
                    .padding(DesignTokens.Spacing.md)
                }
                .frame(height: 80)
                
                // Content
                VStack(alignment: .leading, spacing: DesignTokens.Spacing.sm) {
                    Text(model.name)
                        .font(DesignTokens.Typography.headline)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                    
                    Text(model.description)
                        .font(DesignTokens.Typography.caption1)
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                        .lineLimit(2)
                    
                    // Tags
                    FlowLayout(spacing: DesignTokens.Spacing.xxs) {
                        ForEach(model.tags, id: \.self) { tag in
                            Text(tag)
                                .font(DesignTokens.Typography.caption2)
                                .foregroundColor(DesignTokens.Colors.textSecondary)
                                .padding(.horizontal, DesignTokens.Spacing.xs)
                                .padding(.vertical, 2)
                                .background(
                                    Capsule()
                                        .fill(DesignTokens.Colors.backgroundTertiary)
                                )
                        }
                    }
                    
                    Spacer()
                    
                    // Footer
                    HStack {
                        Text("by \(model.author)")
                            .font(DesignTokens.Typography.caption2)
                            .foregroundColor(DesignTokens.Colors.textTertiary)
                        
                        Spacer()
                        
                        Button("Details") {
                            showingDetails = true
                        }
                        .buttonStyle(DarkModeButtonStyle(variant: .ghost, size: .small))
                    }
                }
                .padding(DesignTokens.Spacing.md)
            }
        }
        .onHover { hovering in
            withAnimation(DesignTokens.Animation.smooth) {
                isHovered = hovering
            }
        }
        .sheet(isPresented: $showingDetails) {
            ModelDetailsSheet(model: model)
        }
    }
}

// MARK: - Model Details Sheet
struct ModelDetailsSheet: View {
    let model: VoiceModel
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Model Details")
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
            
            // Content
            ScrollView {
                VStack(alignment: .leading, spacing: DesignTokens.Spacing.xl) {
                    // Model info sections
                    DetailSection(title: "General Information") {
                        DetailRow(label: "Name", value: model.name)
                        DetailRow(label: "Author", value: model.author)
                        DetailRow(label: "Created", value: model.formattedDate)
                        DetailRow(label: "File Size", value: model.formattedFileSize)
                    }
                    
                    DetailSection(title: "Technical Details") {
                        DetailRow(label: "Sample Rate", value: "\(model.sampleRate) Hz")
                        DetailRow(label: "Model Path", value: model.modelPath)
                        DetailRow(label: "Config Path", value: model.configPath)
                    }
                    
                    DetailSection(title: "Description") {
                        Text(model.description)
                            .font(DesignTokens.Typography.body)
                            .foregroundColor(DesignTokens.Colors.textSecondary)
                    }
                }
                .padding(DesignTokens.Spacing.lg)
            }
        }
        .frame(width: 600, height: 500)
        .background(DesignTokens.Colors.backgroundPrimary)
    }
}

// MARK: - Detail Section
struct DetailSection<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: DesignTokens.Spacing.sm) {
            Text(title)
                .font(DesignTokens.Typography.headline)
                .foregroundColor(DesignTokens.Colors.textPrimary)
            
            content
        }
    }
}

// MARK: - Detail Row
struct DetailRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(DesignTokens.Typography.body)
                .foregroundColor(DesignTokens.Colors.textSecondary)
            
            Spacer()
            
            Text(value)
                .font(DesignTokens.Typography.body)
                .foregroundColor(DesignTokens.Colors.textPrimary)
        }
    }
}

// MARK: - Preview
struct ModelsView_Previews: PreviewProvider {
    static var previews: some View {
        ModelsView()
            .environmentObject(VoiceConverterViewModel())
            .preferredColorScheme(.dark)
            .frame(width: 1200, height: 800)
    }
}