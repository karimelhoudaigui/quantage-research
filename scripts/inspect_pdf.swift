import Foundation
import AppKit
import PDFKit
let args = CommandLine.arguments
if args.count != 3 { fatalError("input PDF and fresh output directory required") }
let input = URL(fileURLWithPath: args[1])
let output = URL(fileURLWithPath: args[2], isDirectory: true)
try FileManager.default.createDirectory(at: output, withIntermediateDirectories: true)
guard let document = PDFDocument(url: input) else { fatalError("Unreadable PDF") }
var extracted = ""
for index in 0..<document.pageCount {
    guard let page = document.page(at: index) else { fatalError("Missing page") }
    extracted += "\n--- PAGE \(index+1) ---\n" + (page.string ?? "")
    let thumb = page.thumbnail(of: NSSize(width: 1200, height: 1700), for: .mediaBox)
    guard let tiff = thumb.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiff),
          let png = bitmap.representation(using: .png, properties: [:]) else { fatalError("Rasterization failed") }
    try png.write(to: output.appendingPathComponent(String(format:"page-%02d.png", index+1)))
}
try extracted.write(to: output.appendingPathComponent("text.txt"), atomically: true, encoding: .utf8)
print("Rendered \(document.pageCount) PDF pages and extracted text")
