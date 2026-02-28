import Foundation

/// 백엔드 API 클라이언트 (추후 실제 엔드포인트 연동)
enum ApiService {
    private static let baseURL = "http://localhost:8000"

    static func fetchDeals() async throws -> [Deal] {
        guard let url = URL(string: "\(baseURL)/api/deals") else {
            throw ApiError.invalidURL
        }
        let (data, _) = try await URLSession.shared.data(from: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try decoder.decode([Deal].self, from: data)
    }
}

enum ApiError: Error {
    case invalidURL
    case decodingFailed
}
