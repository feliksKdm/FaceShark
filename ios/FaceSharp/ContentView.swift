//
//  ContentView.swift
//  FaceSharp
//
//  Created for FaceSharp
//

import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = FaceAnalysisViewModel()
    @State private var showImagePicker = false
    @State private var imagePickerSourceType: UIImagePickerController.SourceType = .photoLibrary
    
    var body: some View {
        NavigationView {
            ZStack {
                // Background gradient
                LinearGradient(
                    colors: [Color(red: 0.4, green: 0.49, blue: 0.92), Color(red: 0.46, green: 0.29, blue: 0.64)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Header
                        VStack(spacing: 8) {
                            Text("🎯 FaceSharp")
                                .font(.system(size: 48, weight: .bold))
                                .foregroundColor(.white)
                            Text("Оценка качества селфи с мем-лейблами")
                                .font(.subheadline)
                                .foregroundColor(.white.opacity(0.9))
                        }
                        .padding(.top, 20)
                        
                        // Main content card
                        VStack(spacing: 20) {
                            // Image section
                            if let image = viewModel.selectedImage {
                                Image(uiImage: image)
                                    .resizable()
                                    .scaledToFit()
                                    .frame(maxHeight: 400)
                                    .cornerRadius(16)
                                    .shadow(radius: 8)
                            } else {
                                ImagePlaceholderView()
                            }
                            
                            // Action buttons
                            HStack(spacing: 16) {
                                Button(action: {
                                    imagePickerSourceType = .photoLibrary
                                    showImagePicker = true
                                }) {
                                    Label("Галерея", systemImage: "photo.on.rectangle")
                                        .frame(maxWidth: .infinity)
                                        .padding()
                                        .background(Color.blue)
                                        .foregroundColor(.white)
                                        .cornerRadius(12)
                                }
                                
                                Button(action: {
                                    imagePickerSourceType = .camera
                                    showImagePicker = true
                                }) {
                                    Label("Камера", systemImage: "camera")
                                        .frame(maxWidth: .infinity)
                                        .padding()
                                        .background(Color.green)
                                        .foregroundColor(.white)
                                        .cornerRadius(12)
                                }
                            }
                            .padding(.horizontal)
                            
                            // Analyze button
                            if viewModel.selectedImage != nil {
                                Button(action: {
                                    viewModel.analyzeImage()
                                }) {
                                    if viewModel.isAnalyzing {
                                        ProgressView()
                                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                            .frame(maxWidth: .infinity)
                                            .padding()
                                            .background(Color.purple)
                                            .cornerRadius(12)
                                    } else {
                                        Text("Анализировать")
                                            .frame(maxWidth: .infinity)
                                            .padding()
                                            .background(Color.purple)
                                            .foregroundColor(.white)
                                            .cornerRadius(12)
                                            .font(.headline)
                                    }
                                }
                                .padding(.horizontal)
                                .disabled(viewModel.isAnalyzing)
                            }
                            
                            // Results section
                            if let result = viewModel.result {
                                ResultView(result: result)
                            }
                            
                            // Error message
                            if let error = viewModel.error {
                                Text(error)
                                    .foregroundColor(.red)
                                    .padding()
                                    .background(Color.red.opacity(0.1))
                                    .cornerRadius(8)
                                    .padding(.horizontal)
                            }
                        }
                        .padding()
                        .background(Color.white)
                        .cornerRadius(20)
                        .shadow(radius: 10)
                        .padding(.horizontal)
                    }
                    .padding(.bottom, 40)
                }
            }
            .navigationBarHidden(true)
            .sheet(isPresented: $showImagePicker) {
                ImagePicker(
                    sourceType: imagePickerSourceType,
                    selectedImage: $viewModel.selectedImage
                )
            }
        }
    }
}

struct ImagePlaceholderView: View {
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "photo")
                .font(.system(size: 64))
                .foregroundColor(.gray)
            Text("Выберите фото для анализа")
                .font(.headline)
                .foregroundColor(.gray)
        }
        .frame(height: 200)
        .frame(maxWidth: .infinity)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(16)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

