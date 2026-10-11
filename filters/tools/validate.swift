// WebKitで実際にルールJSONをコンパイルして、Safariが読み込めるか確かめる。
//   swift filters/tools/validate.swift filters/public/scam.json filters/public/ads.json ...
import Foundation
import WebKit

let dir = FileManager.default.temporaryDirectory.appendingPathComponent("seadice-filter-validate-\(UUID().uuidString)")
try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
guard let store = WKContentRuleListStore(url: dir) else { print("store error"); exit(2) }
var failed = false
for path in CommandLine.arguments.dropFirst() {
    let json = try! String(contentsOfFile: path, encoding: .utf8)
    let start = Date()
    var done = false
    DispatchQueue.main.async {
        store.compileContentRuleList(forIdentifier: UUID().uuidString, encodedContentRuleList: json) { list, error in
            let sec = String(format: "%.1f", Date().timeIntervalSince(start))
            if let error { print("NG \(path) (\(sec)s): \(error)"); failed = true } else { print("OK \(path) (\(sec)s)") }
            done = true
        }
    }
    while !done { RunLoop.main.run(until: Date().addingTimeInterval(0.1)) }
}
try? FileManager.default.removeItem(at: dir)
exit(failed ? 1 : 0)
