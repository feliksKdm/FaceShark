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
        case "mogged":
            return .green
        case "sigma":
            return .blue
        case "meh":
            return .orange
        default:
            return .gray
        }
    }
    
    var labelText: String {
        switch result.label?.lowercased() {
        case "mogged":
            return "MOGGED"
        case "sigma":
            return "SIGMA"
        case "meh":
            return "MEH"
        default:
            return result.label?.uppercased() ?? "UNKNOWN"
        }
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
                
                if let confidence = result.confidence {
                    Text("Уверенность: \(Int(confidence * 100))%")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
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

