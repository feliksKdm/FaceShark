//
//  ResultView.swift
//  FaceSharp
//
//  Created for FaceSharp
//

import SwiftUI

struct ResultView: View {
    let result: AnalysisResult
    
    var labelColor: Color {
        switch result.label?.lowercased() {
        case "god":
            return Color(red: 0.55, green: 0.36, blue: 0.96) // purple
        case "mogged":
            return .green
        case "sigma":
            return .blue
        case "average":
            return .yellow
        case "meh":
            return .orange
        case "trash":
            return .red
        default:
            return .gray
        }
    }
    
    var labelText: String {
        switch result.label?.lowercased() {
        case "god":
            return "GOD"
        case "mogged":
            return "MOGGED"
        case "sigma":
            return "SIGMA"
        case "average":
            return "AVERAGE"
        case "meh":
            return "MEH"
        case "trash":
            return "TRASH"
        default:
            return result.label?.uppercased() ?? "UNKNOWN"
        }
    }
    
    func getTagLabel(_ tag: String) -> String {
        let tagLabels: [String: String] = [
            "very_blurry": "Очень размыто",
            "blurry": "Размыто",
            "dark": "Темно",
            "overexposed": "Переэкспонировано",
            "bad_pose": "Плохая поза",
            "weak_jaw": "Слабая челюсть",
            "low_contrast": "Низкий контраст"
        ]
        return tagLabels[tag] ?? tag
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Label badge
            HStack {
                Text(labelText)
                    .font(.system(size: 24, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 12)
                    .background(labelColor)
                    .cornerRadius(30)
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    if let confidence = result.confidence {
                        Text("Уверенность: \(Int(confidence * 100))%")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    if let quality = result.quality {
                        Text("Качество: \(String(format: "%.1f", quality))")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                }
            }
            
            // Tags
            if let tags = result.tags, !tags.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(tags, id: \.self) { tag in
                            Text(getTagLabel(tag))
                                .font(.caption)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 6)
                                .background(Color.gray.opacity(0.2))
                                .cornerRadius(8)
                        }
                    }
                }
                .padding(.vertical, 8)
            }
            
            // Axes bars
            if let axes = result.axes {
                VStack(spacing: 12) {
                    AxisBarView(label: "Резкость", value: axes.sharpness ?? 0, color: labelColor)
                    AxisBarView(label: "Освещение", value: axes.lighting ?? 0, color: labelColor)
                    AxisBarView(label: "Поза", value: axes.pose ?? 0, color: labelColor)
                    AxisBarView(label: "Челюсть", value: axes.jawline ?? 0, color: labelColor)
                    AxisBarView(label: "Контраст", value: axes.contrast ?? 0, color: labelColor)
                }
            }
            
            // Reasons
            if let reasons = result.reasons, !reasons.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Причины оценки:")
                        .font(.headline)
                    ForEach(reasons, id: \.self) { reason in
                        HStack(alignment: .top, spacing: 8) {
                            Text("•")
                                .foregroundColor(labelColor)
                            Text(reason)
                                .font(.subheadline)
                        }
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(8)
            }
            
            // Abstain warning
            if result.abstain == true {
                Text("Недостаточно данных для точной оценки")
                    .font(.subheadline)
                    .foregroundColor(.orange)
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .cornerRadius(8)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(16)
    }
}

struct AxisBarView: View {
    let label: String
    let value: Double
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(label)
                    .font(.subheadline)
                    .fontWeight(.medium)
                Spacer()
                Text("\(Int(value))")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(.secondary)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Rectangle()
                        .fill(Color.gray.opacity(0.2))
                        .frame(height: 8)
                        .cornerRadius(4)
                    
                    Rectangle()
                        .fill(color)
                        .frame(width: geometry.size.width * CGFloat(value / 100), height: 8)
                        .cornerRadius(4)
                }
            }
            .frame(height: 8)
        }
    }
}

