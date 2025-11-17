// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "IndustriverseSDK",
    platforms: [
        .iOS(.v15),
        .macOS(.v12),
        .watchOS(.v8),
        .tvOS(.v15)
    ],
    products: [
        .library(
            name: "IndustriverseSDK",
            targets: ["IndustriverseSDK"]),
    ],
    targets: [
        .target(
            name: "IndustriverseSDK",
            dependencies: []),
        .testTarget(
            name: "IndustriverseSDKTests",
            dependencies: ["IndustriverseSDK"]),
    ]
)
