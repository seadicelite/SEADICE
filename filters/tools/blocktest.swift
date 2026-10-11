// 実際にWebKitでページを開き、ルールが止めるか確かめる。
//   swift filters/tools/blocktest.swift <rules.json> <url> [<url>...]
// 結果: BLOCKED（ブロッカーが止めた）/ LOADED / ERROR（ブロッカー以外の失敗。DNSなど）
import Foundation
import WebKit

final class Nav: NSObject, WKNavigationDelegate {
    var result: String?
    func webView(_ w: WKWebView, didFinish n: WKNavigation!) { result = "LOADED" }
    func webView(_ w: WKWebView, didFail n: WKNavigation!, withError e: Error) { result = classify(e) }
    func webView(_ w: WKWebView, didFailProvisionalNavigation n: WKNavigation!, withError e: Error) { result = classify(e) }
    func classify(_ e: Error) -> String {
        let ns = e as NSError
        return ns.domain == "WebKitErrorDomain" && ns.code == 104 ? "BLOCKED" : "ERROR(\(ns.domain) \(ns.code))"
    }
}

func wait(_ cond: () -> Bool, _ sec: Double) {
    let end = Date().addingTimeInterval(sec)
    while !cond() && Date() < end { RunLoop.main.run(until: Date().addingTimeInterval(0.05)) }
}

let args = Array(CommandLine.arguments.dropFirst())
let json = try! String(contentsOfFile: args[0], encoding: .utf8)
var list: WKContentRuleList?
WKContentRuleListStore.default().compileContentRuleList(forIdentifier: "test-\(UUID())", encodedContentRuleList: json) { l, e in
    if let e { print("compile error", e); exit(2) }
    list = l
}
wait({ list != nil }, 60)
let config = WKWebViewConfiguration()
config.userContentController.add(list!)
let web = WKWebView(frame: .init(x: 0, y: 0, width: 800, height: 600), configuration: config)
for url in args.dropFirst() {
    let nav = Nav()
    web.navigationDelegate = nav
    web.load(URLRequest(url: URL(string: url)!))
    wait({ nav.result != nil }, 20)
    print(nav.result ?? "TIMEOUT", url)
}
