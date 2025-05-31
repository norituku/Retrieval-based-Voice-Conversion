//
//  HistoryView.swift
//  VoiceConverterMac
//
//  Conversion History Interface
//

import SwiftUI

struct HistoryView: View {
    @EnvironmentObject var viewModel: VoiceConverterViewModel
    @State private var selectedTask: ConversionTask?
    @State private var searchText = ""
    @State private var selectedDateRange = DateRange.all
    
    enum DateRange: String, CaseIterable {
        case all = "All Time"
        case today = "Today"
        case week = "This Week"
        case month = "This Month"
        
        var dateInterval: DateInterval? {
            let calendar = Calendar.current
            let now = Date()
            
            switch self {
            case .all:
                return nil
            case .today:
                let start = calendar.startOfDay(for: now)
                return DateInterval(start: start, end: now)
            case .week:
                let start = calendar.dateInterval(of: .weekOfYear, for: now)?.start ?? now
                return DateInterval(start: start, end: now)
            case .month:
                let start = calendar.dateInterval(of: .month, for: now)?.start ?? now
                return DateInterval(start: start, end: now)
            }
        }
    }
    
    var filteredTasks: [ConversionTask] {
        viewModel.conversionTasks.filter { task in
            let matchesSearch = searchText.isEmpty ||
                task.inputFile.fileName.localizedCaseInsensitiveContains(searchText) ||
                task.model.name.localizedCaseInsensitiveContains(searchText)
            
            let matchesDate = true // Add date filtering logic here
            
            return matchesSearch && matchesDate
        }
    }
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            headerSection
            
            DarkModeDivider(orientation: .horizontal)
            
            // Content
            if filteredTasks.isEmpty {
                emptyState
            } else {
                historyList
            }
        }
    }
    
    private var headerSection: some View {
        VStack(spacing: DesignTokens.Spacing.lg) {
            // Title
            HStack {
                VStack(alignment: .leading, spacing: DesignTokens.Spacing.xs) {
                    Text("Conversion History")
                        .font(DesignTokens.Typography.largeTitle)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                    
                    Text("\(viewModel.conversionTasks.count) conversions")
                        .font(DesignTokens.Typography.body)
                        .foregroundColor(DesignTokens.Colors.textSecondary)
                }
                
                Spacer()
                
                // Date Range Picker
                Picker("", selection: $selectedDateRange) {
                    ForEach(DateRange.allCases, id: \.self) { range in
                        Text(range.rawValue).tag(range)
                    }
                }
                .pickerStyle(SegmentedPickerStyle())
                .frame(width: 300)
            }
            
            // Search
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(DesignTokens.Colors.textSecondary)
                
                TextField("Search conversions...", text: $searchText)
                    .textFieldStyle(.plain)
                    .foregroundColor(DesignTokens.Colors.textPrimary)
            }
            .padding(DesignTokens.Spacing.sm)
            .background(
                RoundedRectangle(cornerRadius: DesignTokens.CornerRadius.medium)
                    .fill(DesignTokens.Colors.backgroundSecondary)
            )
            .frame(maxWidth: 400)
        }
        .padding(DesignTokens.Spacing.xxl)
    }
    
    private var historyList: some View {
        ScrollView {
            LazyVStack(spacing: DesignTokens.Spacing.sm) {
                ForEach(filteredTasks) { task in
                    HistoryRow(task: task, isSelected: selectedTask?.id == task.id) {
                        selectedTask = task
                    }
                }
            }
            .padding(DesignTokens.Spacing.xxl)
        }
    }
    
    private var emptyState: some View {
        VStack(spacing: DesignTokens.Spacing.lg) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 64))
                .foregroundColor(DesignTokens.Colors.textTertiary)
            
            Text("No conversions yet")
                .font(DesignTokens.Typography.headline)
                .foregroundColor(DesignTokens.Colors.textSecondary)
            
            Text("Your conversion history will appear here")
                .font(DesignTokens.Typography.body)
                .foregroundColor(DesignTokens.Colors.textTertiary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - History Row
struct HistoryRow: View {
    @ObservedObject var task: ConversionTask
    let isSelected: Bool
    let action: () -> Void
    
    @State private var isHovered = false
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: DesignTokens.Spacing.md) {
                // Status Icon
                ZStack {
                    Circle()
                        .fill(statusColor.opacity(0.2))
                        .frame(width: 40, height: 40)
                    
                    Image(systemName: statusIcon)
                        .foregroundColor(statusColor)
                        .font(.system(size: 16))
                }
                
                // File Info
                VStack(alignment: .leading, spacing: DesignTokens.Spacing.xxs) {
                    Text(task.inputFile.fileName)
                        .font(DesignTokens.Typography.bodyBold)
                        .foregroundColor(DesignTokens.Colors.textPrimary)
                        .lineLimit(1)
                    
                    HStack(spacing: DesignTokens.Spacing.sm) {
                        Label(task.model.name, systemImage: "cube.box")
                        Label(task.inputFile.formattedDuration, systemImage: "clock")
                    }
                    .font(DesignTokens.Typography.caption1)
                    .foregroundColor(DesignTokens.Colors.textSecondary)
                }
                
                Spacer()
                
                // Actions
                HStack(spacing: DesignTokens.Spacing.sm) {
                    if case .completed = task.status {
                        IconButton(icon: "play.circle", size: 32) {
                            // Play action
                        }
                        
                        IconButton(icon: "square.and.arrow.down", size: 32) {
                            // Download action
                        }
                    }
                    
                    IconButton(icon: "arrow.right.circle", size: 32) {
                        // Show details
                    }
                }
            }
            .padding(DesignTokens.Spacing.md)
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
    
    private var statusIcon: String {
        switch task.status {
        case .pending: return "clock"
        case .processing: return "arrow.triangle.2.circlepath"
        case .completed: return "checkmark.circle"
        case .failed: return "xmark.circle"
        case .cancelled: return "xmark.circle"
        }
    }
    
    private var statusColor: Color {
        switch task.status {
        case .pending: return DesignTokens.Colors.textSecondary
        case .processing: return DesignTokens.Colors.accentPrimary
        case .completed: return DesignTokens.Colors.success
        case .failed: return DesignTokens.Colors.error
        case .cancelled: return DesignTokens.Colors.textTertiary
        }
    }
}

// MARK: - Preview
struct HistoryView_Previews: PreviewProvider {
    static var previews: some View {
        HistoryView()
            .environmentObject(VoiceConverterViewModel())
            .preferredColorScheme(.dark)
            .frame(width: 1200, height: 800)
    }
}