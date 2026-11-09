// 画像の文字を Mac の Vision で読み、1枚ごとに「パス\t読んだ文字（改行は空白）」を1行で出す。
// scripts/mockup.py が、実画面に価格の言葉（Guideline 2.3.7）が映っていないかを確かめるのに使う。
//   swift scripts/ocr.swift a.png b.png ...
import Foundation
import Vision

for path in CommandLine.arguments.dropFirst() {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["ja-JP", "en-US"]
    request.usesLanguageCorrection = false
    let handler = VNImageRequestHandler(url: URL(fileURLWithPath: path))
    var lines: [String] = []
    do {
        try handler.perform([request])
        for obs in request.results ?? [] {
            if let top = obs.topCandidates(1).first { lines.append(top.string) }
        }
    } catch {
        FileHandle.standardError.write("読めません: \(path) \(error)\n".data(using: .utf8)!)
    }
    print("\(path)\t\(lines.joined(separator: " "))")
}
