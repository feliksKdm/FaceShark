//
//  FaceAnalysisViewModel.swift
//  FaceSharp
//
//  Created for FaceSharp
//

import SwiftUI
import Combine

class FaceAnalysisViewModel: ObservableObject {
    @Published var selectedImage: UIImage?
    @Published var result: AnalysisResult?
    @Published var isAnalyzing = false
    @Published var error: String?
    
    // API endpoint - change to your backend URL
    private let apiURL = "http://localhost:8000/analyze"
    
    func analyzeImage() {
        guard let image = selectedImage else { return }
        
        isAnalyzing = true
        error = nil
        result = nil
        
        // Convert UIImage to JPEG data
        guard let imageData = image.jpegData(compressionQuality: 0.8) else {
            error = "Не удалось обработать изображение"
            isAnalyzing = false
            return
        }
        
        // Create multipart form data request
        var request = URLRequest(url: URL(string: apiURL)!)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        // Perform request
        URLSession.shared.dataTask(with: request) { [weak self] data, response, error in
            DispatchQueue.main.async {
                self?.isAnalyzing = false
                
                if let error = error {
                    self?.error = "Ошибка сети: \(error.localizedDescription)"
                    return
                }
                
                guard let data = data else {
                    self?.error = "Нет данных от сервера"
                    return
                }
                
                do {
                    let result = try JSONDecoder().decode(AnalysisResult.self, from: data)
                    self?.result = result
                } catch {
                    self?.error = "Ошибка парсинга: \(error.localizedDescription)"
                }
            }
        }.resume()
    }
}

// MARK: - Data Models

struct AnalysisResult: Codable {
    let ok: Bool
    let axes: Axes?
    let label: String?
    let confidence: Double?
    let reasons: [String]?
    let tags: [String]?
    let quality: Double?
    let abstain: Bool?
    let modelVersion: String?
    
    enum CodingKeys: String, CodingKey {
        case ok, axes, label, confidence, reasons, tags, quality, abstain
        case modelVersion = "model_version"
    }
}

struct Axes: Codable {
    let sharpness: Double?
    let lighting: Double?
    let pose: Double?
    let jawline: Double?
    let contrast: Double?
}

