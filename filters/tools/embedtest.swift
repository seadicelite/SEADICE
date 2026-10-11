// 普通のページに広告・追跡のスクリプトを埋め込み、ルールで止まるか確かめる。
//   swift filters/tools/embedtest.swift <rules.json> <script-url> [...]
import Foundation
import WebKit

func wait(_ cond: () -> Bool, _ sec: Double) {
    let end = Date().addingTimeInterval(sec)
    while !cond() && Date() < end { RunLoop.main.run(until: Date().addingTimeInterval(0.05)) }
}
let args = Array(CommandLine.arguments.dropFirst())
var list: WKContentRuleList?
WKContentRuleListStore.default().compileContentRuleList(forIdentifier: "embed-\(UUID())", encodedContentRuleList: try! String(contentsOfFile: args[0], encoding: .utf8)) { l, e in
    if let e { print("compile error", e); exit(2) }
    list = l
}
wait({ list != nil }, 60)
let config = WKWebViewConfiguration()
config.userContentController.add(list!)
let web = WKWebView(frame: .init(x: 0, y: 0, width: 800, height: 600), configuration: config)
for src in args.dropFirst() {
    let html = "<html><body><script>window.r='PENDING'</script><script src='\(src)' onload=\"window.r='LOADED'\" onerror=\"window.r='BLOCKED'\"></script></body></html>"
    web.loadHTMLString(html, baseURL: URL(string: "https://example.com/")!)
    var r = "PENDING"
    let end = Date().addingTimeInterval(15)
    while r == "PENDING" && Date() < end {
        RunLoop.main.run(until: Date().addingTimeInterval(0.3))
        web.evaluateJavaScript("window.r") { v, _ in if let s = v as? String { r = s } }
    }
    print(r, src)
}
