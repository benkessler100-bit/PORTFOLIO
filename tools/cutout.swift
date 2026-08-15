// Lift the foreground subject out of a photo (same engine as Preview's "Remove Background")
// and write a transparent PNG. Usage: cutout <in.jpg> <out.png>
import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count == 3 else { print("usage: cutout <in> <out>"); exit(1) }
let inURL = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])

guard let src = CIImage(contentsOf: inURL) else { print("cannot read input"); exit(1) }

let handler = VNImageRequestHandler(url: inURL, options: [:])
let req = VNGenerateForegroundInstanceMaskRequest()

do {
    try handler.perform([req])
    guard let obs = req.results?.first else { print("no subject found"); exit(2) }
    print("instances: \(obs.allInstances.count)")
    let masked = try obs.generateMaskedImage(ofInstances: obs.allInstances,
                                             from: handler,
                                             croppedToInstancesExtent: true)
    let ci = CIImage(cvPixelBuffer: masked)
    let ctx = CIContext()
    guard let png = ctx.pngRepresentation(of: ci,
                                          format: .RGBA8,
                                          colorSpace: CGColorSpaceCreateDeviceRGB()) else {
        print("encode failed"); exit(1)
    }
    try png.write(to: outURL)
    print("wrote \(outURL.path) — \(Int(ci.extent.width))x\(Int(ci.extent.height))")
} catch {
    print("error: \(error)")
    exit(1)
}
