import Foundation

/// 항공 특가·이벤트 한 건 (백엔드 API 응답과 매핑)
struct Deal: Codable, Identifiable {
    let id: String
    let airline: String
    let title: String
    let description: String?
    let url: String
    let imageUrl: String?
    let startDate: Date?
    let endDate: Date?
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id, airline, title, description, url
        case imageUrl = "image_url"
        case startDate = "start_date"
        case endDate = "end_date"
        case createdAt = "created_at"
    }
}
