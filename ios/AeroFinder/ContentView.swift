import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            VStack {
                Text("AeroFinder")
                    .font(.title)
                Text("항공사 특가 이벤트")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
            .navigationTitle("AeroFinder")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    ContentView()
}
