// Control-unit names by diagnostic address, for the all-modules fault scan.
// From idrive7-apps kit/runtime/ecus.js (MIT, see third-party/idrive7-apps-LICENSE), which combines a
// G20 330e's own unit list with F-series addresses, adjusted here to F-series unit names.
// An address another car uses differently keeps its name: confirm a unit before acting on a code.
#ifndef ECU_NAMES_H
#define ECU_NAMES_H

static const struct EcuName {
    unsigned address;
    const char* name;
} kEcuNames[] = {
    {0x01, "ACSM airbag"}, {0x06, "ICAM cameras"}, {0x07, "SME HV battery"}, {0x08, "SRR corner radar"},
    {0x0D, "HKFM tailgate"}, {0x10, "ZGW gateway"}, {0x12, "DME engine"}, {0x13, "DME 2"},
    {0x14, "SLE/OBC charger"}, {0x18, "EGS gearbox"}, {0x1A, "EME e-motor"}, {0x1D, "TFM fuel tank"},
    {0x20, "SRR corner radar"}, {0x21, "FRR front radar"}, {0x23, "SAS assist sensors"},
    {0x28, "SRR corner radar"}, {0x29, "DSC brakes"}, {0x2A, "SRR corner radar"},
    {0x2C, "USS park sensors"}, {0x30, "EPS steering"}, {0x37, "RAM audio"}, {0x38, "VTG xDrive"},
    {0x39, "DSC brake booster"}, {0x3A, "EME e-motor"}, {0x40, "FEM body"}, {0x43, "FLM headlight"},
    {0x44, "FLM headlight"}, {0x45, "DCS driver camera"}, {0x56, "FZD roof"}, {0x5D, "KAFAS camera"},
    {0x5E, "GWS gear selector"}, {0x60, "KOMBI cluster"}, {0x61, "ATM telematics"}, {0x63, "Head unit"},
    {0x64, "PDC parking"}, {0x67, "ZBE controller"}, {0x6D, "SM seat module"}, {0x72, "FRM footwell"},
    {0x76, "VDP dampers"}, {0x78, "IHKA climate"},
};

static inline const char* ecu_name(unsigned address) {
    for (unsigned i=0;i<sizeof kEcuNames/sizeof kEcuNames[0];++i)
        if (kEcuNames[i].address==address) return kEcuNames[i].name;
    return 0;
}

#endif
