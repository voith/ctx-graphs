from collections import defaultdict
from datetime import datetime
from io import BytesIO
from itertools import count

import xlsxwriter
from sqlalchemy.orm import Session

from models import (
    TransferEvent,
    SushiSwapSwapEvent,
    SushiSwapMintEvent,
    SushiSwapBurnEvent,
    Address,
    engine,
)

CTX_DEPLOYER = "0x1A14F9367Db41400BE5d38a0bC48d4Cc2e4B7157"
CTX_ADDRESS = "0x321c2fe4446c7c963dc41dd58879af648838f98d"

DELEGATORS = [
    "0xbd291b8dc2ff25544b5ed19bddc4aefc58c1ad1a",
    "0x833951a226532d48ec15ce403fa30af6a17d71e9",
    "0xb119b634a44d2cf7f586276b91e5568127980ad4",
    "0xc48d130f53c731358ecb4993ee9f49318b24ebd3",
    "0x836903ba32914ae9ed8c81e5875842061b53e8c5",
    "0x082136d31f528528c1d63cec121dd6c6b16b6fde",
    "0x29ee31361492a77baa6511d43c600e89de08c954",
    "0x571b9b70b121d2e64aa92c10d74446dd63c81376",
]
DELEGATOR_FACTORY = "0x70236b36f86ab4bd557fe9934e1246537b472918"
TIMELOCK = "0xa54074b2cc0e96a43048d4a68472f7f046ac0da8"
TREASURY_VESTER = [
    "0xa62a082bb8f9f0e63f69053f070fa5c12df1c07e",
    "0x7059928231d115bb47d46fdfd5e574c5e4fe38c0",
    "0x2121b3f1719a90e4ded5918cf24a2cc9fca4f1c5",
]
REWARD_HANDLERS = [
    "0xdc4cdd5db9ee777efd891690dc283638cb3a5f94",
    "0xc8bb1cd417d20116387a5e0603e195ca4f3cf59a",
    "0xe0c99c503c4ae5ec50ac63c59c7ef4725c355fdd",
]

CRYPTEX_OWNED_ADDRESSES = [
    CTX_DEPLOYER,
    DELEGATOR_FACTORY,
    TIMELOCK
] + DELEGATORS + TREASURY_VESTER + REWARD_HANDLERS

SUSHISWAP_CTX_POOL = "0x2a93167ed63a31f35ca4788e2eb9fbd9fa6089d0"
SUSHISWAP_ROUTER = "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f"
TCAP_SUSHISWAP = "0xa87e2c5d5964955242989b954474ff2eb08dd2f5"
TCAP_UNISWAP = "0x11456b3750e991383bb8943118ed79c1afdee192"
UNISWAP_NFT = "0xc36442b4a4522e871399cd717abdd847ab11fe88"
TCAP_LIQUIDITY_REWARD = "0xc8bb1cd417d20116387a5e0603e195ca4f3cf59a"
TCAP = "0x16c52CeeCE2ed57dAd87319D91B5e3637d50aFa4"

ADDR_T0_IGNORE = set(CRYPTEX_OWNED_ADDRESSES + [
 SUSHISWAP_CTX_POOL,
 SUSHISWAP_ROUTER,
 TCAP_SUSHISWAP,
 TCAP_UNISWAP,
 UNISWAP_NFT,
 TCAP_LIQUIDITY_REWARD,
 TCAP,
])

CONTRACT_ADDRESSES = []

ACTUAL_BALANCE = defaultdict(int)
TOTAL_BALANCE = defaultdict(int)
STAKED_BALANCE = defaultdict(int)
SUSHI_STAKED_BALANCE = defaultdict(int)
TOTAL_HOLDING_DAYS = defaultdict(int)
LAST_HOLDING_DATE = defaultdict(lambda: None)

MY_ADDR = "0x94479f0e32c3397f9be5521184cacad1bc0fc0f3"

locked_date = datetime.utcfromtimestamp(1663617405)

suspicious_addresses = {'0x000018bbb8df8de9e3eaf772db1c4eec228ef06c',
 '0x0000f079e68bbcc79ab9600ace786b0a4db1c83c',
 '0x0032311e56bc34efde20b408bb99d986eea1863a',
 '0x006bd85b018f599422c02b5a5833107fc0e93f0f',
 '0x017a0583d4a29137a5649b5d330c5a24cbc01213',
 '0x01a2756ed2761380831a7f76f8e82d2501afe7f9',
 '0x01c3dd0607e189d8ec94c740cf5926db4f38bf3f',
 '0x02331822991971bd590430b2f276ebda8cebb952',
 '0x045e2a9db6ca319f6b667813c6088067eb52851e',
 '0x04d1b927140306a481655a1fe97a319915881af9',
 '0x05cedd3fdaa8997f9300526ff6a354b8654ad0a9',
 '0x06c67a74609be3404dc544bbcb9305ee2aa77cd5',
 '0x06e9925d3e8c642371232e7492c3916d6b855aaa',
 '0x0848f011d99c5aa0abf0e8a43c72d8b573383f2b',
 '0x08bfb6100bffa123b66af10f89b6aa8e26b909c3',
 '0x09a93c45b57844fd32af543d9bc543bb06e21ec4',
 '0x0a2df140af4cf82591e76d21c79e37027714b941',
 '0x0ac235b5082add9879eb47368dcebb314fdd3d08',
 '0x0afed9f9d30a6d788b25b263076cca600cc486d0',
 '0x0b0e217c78d8b5dea04a974cd14a5c27ba7b8487',
 '0x0c5a2c72c009252f0e7312f5a1ab87de02be6fbe',
 '0x0cb961e87f6b7a7ce4e92d1ba653e2a2b5b1d9b9',
 '0x0d03b09e037adf9a9330d0febb055f76eaf11a08',
 '0x0d4a8621a93f20852054e93868b948d8957488e8',
 '0x0d4ec3dbe9312d7e11fa0d3d39c4a6b9ed6a64f6',
 '0x0d7d6ee93af0dbfff011096b59d98e5711cf8f73',
 '0x0fa0911f3323126db7c897a54bcac983e6075266',
 '0x0fdc77a3432fcdd187b19a820aafd5225915edca',
 '0x10ce1b511312e182510afd027e954bacceabc032',
 '0x10d4841e0157078df777c8621a36f18fd771529b',
 '0x1128cdb6df17e282ce448e7770d0f02ce1299e1a',
 '0x1160387a36953afc5d80c0ea7b6b5447774af8e5',
 '0x11ab03a22a17b4b51093b3151c7034c98c38696e',
 '0x12079cc0cf98f66bccfa3332d4cb8bc5d3a53db7',
 '0x12b68d3800ec19917c63ee6759a43b76726d186d',
 '0x137c0bc33dd5687fe2778a6600c52882bef9ad89',
 '0x1414c9744d7eb154487661288ecb99a675bc466b',
 '0x141fef8cd8397a390afe94846c8bd6f4ab981c48',
 '0x145dd77c0eb627b7b93ceabecad82472e424b0f5',
 '0x14b5bd35a245c42a4ad9bf7b46942a6f74bb6fb8',
 '0x1562ee6f474e19287ec68beddd730cfb8f60e74c',
 '0x15903df309f04d1e4944ceb27499301c7e6d8e55',
 '0x1611c227725c5e420ef058275ae772b41775e261',
 '0x163ee09deeea9dab68df0ae49f48c8e07ad54aa2',
 '0x174202b13c0aa0a0da9d59cadc03659637ea8689',
 '0x181d875f83777bf10c71f16e0250c823448c4141',
 '0x183fc0eba0b1485a6bfe1fa7961cd0293b0d3f7b',
 '0x188502b2c3cf130b46ca18f9e35147c16685e9d2',
 '0x1900eb03efbc633d9ab2f23bad0acb7109415d6e',
 '0x19131c3aa44a344396492c85e4858b7505a794e6',
 '0x19323a6c0aa8c6f420e7b3f68a83f4be5d8afaaa',
 '0x197a78fe1bd3bbb64c1325c027bde8f67bac1770',
 '0x199f4550f0251008852996080ac9e21a6c8d8d7f',
 '0x19d43e1620f9fe4ad27649ebd847fde7a2a6a6a8',
 '0x1a03bd7e919004acc9f044caabd20ad596b3bd55',
 '0x1ad80107bbd5cd390d69ef029ff6ff3e79af4d57',
 '0x1b89c2521f3b8a7e4443fc3a9140123ae9db1d1a',
 '0x1b929e3f52c3d1666cddac4f93484067bf83ae31',
 '0x1bedf678ea91476731ee1b32ff8111bb1e822251',
 '0x1bfecdfab4787338f0998ddfee85e78dd25e06a4',
 '0x1c3673876f3e861365f2901544c648fe356a3c55',
 '0x1caf3ee0c5b9547db6e63199cab801b7f7050275',
 '0x1cc00cc60f0b031bb8d460358e27ab2857a07c0d',
 '0x1d2262c36e141549b9670ac2a98a4e44f7831953',
 '0x1d2c4cd9bee9dfe088430b95d274e765151c32db',
 '0x1d7f03aa7f0aa5ef5df68f0f46a72a25f94cccf2',
 '0x1d955a33594e54eb50c9b35b3efecd4bc74d6d5b',
 '0x2133f7b612c452e214dce4270de593390afcf998',
 '0x216dca75358988b53e4b76c497b9068eb8b90d59',
 '0x217c70a564a9bc0572426fc068eff0caf70e6b41',
 '0x21a3a5d357655466dacf4d6efd2a00bbdb939a50',
 '0x21cfe08c7ddb08a8e5fa04baac8b2a1457696731',
 '0x2289d6fd181f9af14f201c8dc81beccb3e05a7e7',
 '0x239eec9ec218f71cef5cc14d88b142ed4ff44110',
 '0x2447807136dc8224e3dd865680b837820d14229e',
 '0x2455dba7f92f3350abc5ee3440e320ea839640d6',
 '0x252b99f1873fb67cc07c092ff7e772c608180f13',
 '0x25599b4c5d678299680c84f904001aa7661d77f7',
 '0x256bb5ad3dbdf61ae08d7cbc0b9223ccb1c60aae',
 '0x26caaf63472a89b1493af295ee50f734a23289b5',
 '0x2829419f7cde7054237ca8610ce29e39bcb0af30',
 '0x28bb9795becf0beb16537bb4f9ff589f942b2f34',
 '0x28f00731408efd5851adbe89748c047fb94abd35',
 '0x294cb241ebf6fe95bbb76071c7cda8dd62eb138e',
 '0x297d0f5e5a4f80a86e0aaf8d26e64d4837be513e',
 '0x2b145ec5f531d3bc836389453b8a3b8348c4ea23',
 '0x2c28295cf6c2e368c09253bdda8bc853a8b83520',
 '0x2cfcd29f49dc97facd08caa0d8ed435660a8f8b6',
 '0x2d46f36579679f2c5be18f89e172b02cbc718ed1',
 '0x2e2370c5794ca1ff1025ff95cc9fa907c91df8cb',
 '0x2e35116f116b94d37efd7c956ed28e1bc00a2517',
 '0x2f9aca9ad59db58b3679a7f4eda342684ac1d518',
 '0x2fffe6c2af66f868ef5305b8fce550478adf6ad5',
 '0x30091d6687c25ad2b83d99214c1802f41bfae688',
 '0x302f039413a84e0c2ea5ae1cc2c57e8093682e1a',
 '0x30645702ad40aed852801a2c403b9c8a3066e03a',
 '0x3096d984158667bb2c371cdebc05d82f2f8ccbdb',
 '0x309b79f4383fa9519f896c38910cf98c63801330',
 '0x30b2ca03f364de2fb10c8b608bbdfbdae5072e7c',
 '0x318f3d84269a4e388916a40b0672547b8c94439e',
 '0x321f602b63338c674b63239821f17a83ef63e5c6',
 '0x3250a2576611f3bfbdead0005b9e3a2a1f6faf50',
 '0x3258f6f758be95adbbfa9cf10d062adebe76709a',
 '0x32ae635f5136adb181a442cc890be39263bc13c8',
 '0x32cf7c2243cf2b615306a72e64ea269b5d54b3e7',
 '0x332ef2adc9e6d980b05a89901f3f29d0464442c5',
 '0x33e88adb8ce6d944ab420e2db4deeca2be0a685c',
 '0x343a6aed149f6412500b6f6bedbe85f3dd23ba91',
 '0x34e31ddb2e1a2e06d8d75f5ea109ce001fc969b5',
 '0x3524b2d9af57d3cf852a5f547152e061aa011139',
 '0x367475e26b3a74b08cc3307b286b8d88e71c3719',
 '0x399532140fb2c066846d18d12720d9f2455fa383',
 '0x399e16866d524124f4c0a000fcbd4486f4f40e94',
 '0x39baaa8cf7ad06e7e0c5a0a2bdcbcfa2b0879fce',
 '0x39c2823148240e2b59d9efc30be1bb385a91ddb1',
 '0x3a021ba306d8e595d120bbb1a0dc05dd9f2af5d9',
 '0x3a61dd9041d0930281bd9cba6c2c1d572a563403',
 '0x3a86499eb85b8459cfa9e0c71e4cc541dcc22e5c',
 '0x3b5c4b1b9f4db1d1e4cddcde0e59c4c2b0d09a31',
 '0x3c22438f13ea9a060c28720a8f50d310fdc30133',
 '0x3c57f6239cf0202436e253170a6e69d54731ad12',
 '0x3cf1a1512149b5e6dd0e29aaffe5400f0848f5d6',
 '0x3d20dd192ab5c63ff6c07f6b8748bd52e62ba329',
 '0x3d6e381035ab5995e06a5b1661ee58e92be755a9',
 '0x3e1218cdeb98db8d6d36775733df1471382a476e',
 '0x3e5eb1f0af98923bad4a0148c6636d6da9671316',
 '0x3e71ec02ab3d9b7fc76047688954bb0a6a9288e1',
 '0x3f0f897ae863b0c2eca8c34d57acc8638dcaa0f6',
 '0x3f68226590db853f0c7154e07f639badb64d83c4',
 '0x4030c68badf1c7e62719e45e6db2d349e8e3d53e',
 '0x40482c0e76e01779b38264d9cc5f94fde9de6e2e',
 '0x41381649b2231cafc8293f501bb3df422aeba5e4',
 '0x418f97beacc5699eb65fbc50ece85a2f6ea89cc0',
 '0x41bc7d0687e6cea57fa26da78379dfdc5627c56d',
 '0x429fc000c964502ee09322f5a5cb250b9d494501',
 '0x431a0015564d357f7ea4fb06e95ce6c0e932a3bf',
 '0x434fe4f12c5093c7c8492f7e8632c39656af8962',
 '0x43764aee49da3d3a877e3326a83bc182a5e0019c',
 '0x438f7bca3c42128840be4c69c1708393fbf375e3',
 '0x43dc87662044e0a7ae1641b0bfaa9066b77275fc',
 '0x43eca8bb221fe9c7a00f746c6c98312b5d7e6318',
 '0x4588b9372e0d8e7d3869fe929d265d9ae2f3ced3',
 '0x46c5c191989aa6631f03c412b41a2715871bce6b',
 '0x46ebb553c048150fb8ac25749e0e521cf27b1bdd',
 '0x4717f20f534c1732a2f987a126181eef5413cad3',
 '0x4730f5dde6daad4b9381f261c9f6f76ce6a9b4d3',
 '0x47c62785133330467304ae83db4b4dd5fbb4ce1b',
 '0x484e2f341f9586e7c07eaf3a6e9150921f9adc09',
 '0x490c71997fbbd5f2ac7a55e185a0f41210b4ab7f',
 '0x4959695595b87d013235a345107a3fdd9b11d1a5',
 '0x499d0bad7a0cc2263c0bfb9d6d76cf80771772a7',
 '0x4ada1b9d9fe28abd9585f58cfeed2169a39e1c6b',
 '0x4afe099b1512cf389acc37d28d74ecd07a52b29e',
 '0x4b1d36f26f609bc62692400cdcd89feab7ea0815',
 '0x4b83d51550e8bb51cbbede919d2786b963ad363c',
 '0x4c889ecadf16e5461ba8feffba94e54c3a63fd04',
 '0x4c9df57276dc17dee5635ded208c07b0be32afd0',
 '0x4cb950f7be4cc14aff4dd975dae4de62e4a56880',
 '0x4cd062ac2f1aa5dabf3b8b7dfdabd8a0dedf3af0',
 '0x4d85e4f760fb58e380f02657ae5aafb8bd010601',
 '0x4d928359e8556197f161f4927a928dfde9c3d1a8',
 '0x4e65175f05b4140a0747c29cce997cd4bb7190d4',
 '0x4f47b0be2df911c8ef35e64fa39f3b1aa2cf2f66',
 '0x4f88c523028d0fa231d6e2df6362aa0b46eacef1',
 '0x4fb0dfc7066a7a942ad608f62611418ef7c0ed26',
 '0x4ff604ce93b73df633b22c0972b8a37cadbc7a91',
 '0x500c908f74114f964127d45d8e8ba02aaf56ba95',
 '0x5137d43da2151aadacadda60b25a13e46ee267c3',
 '0x5185dd278306c3d9b2e20b79e328a311d426c252',
 '0x51ad1db815ccc9de24e7c861c7f6f815db2b8acc',
 '0x51d2dbbcb2ab7b25fa0e47f1c6ca8ce92d9846fe',
 '0x5205527e9fc247f4a185dccd578a527c75addcad',
 '0x521ddba421125b1456b2f09569e51c6ff698a222',
 '0x522a53c6ef7b1eab0db8fcd4bda1a632073118d1',
 '0x53819902e74a6a484097851735b412a3ebf467f7',
 '0x54116f8e2bec28c8d6f9cbb0cadfd1e693bb8da9',
 '0x5466300dd68213613fab49550ae6112a5fd80a3f',
 '0x54c375c481f95ba43e2cecd6ef30631f55518f57',
 '0x54fb0c8ce414d18830b073ae2359e1c3a969a985',
 '0x554c5af96e9e3c05aec01ce18221d0dd25975ab4',
 '0x55b106fd42dffc253394131c0a03398f3e4987ae',
 '0x564bca365d62bcc22db53d032f8dbd35439c9206',
 '0x5698353559cf6da03cb0d3292475022328d4a6ed',
 '0x576816d66a60087f5d155d4ddeeaa3a26b52d450',
 '0x577389c64ad94c6f8fa2fa54972a5827e89bfe42',
 '0x57a974d01ed8677749e8665500000b7ba370022f',
 '0x5815d8951967e202d9b5380fed6c9f0a7fc71c5c',
 '0x5867a5e7e59339c58191334be6c32e6885b6fca6',
 '0x599fa67426da7faa7ffe5ba1e202d58082d7e4de',
 '0x5b356d59ea36ef660173970aa97f76213ba46260',
 '0x5b5ac4512400cf1798c23926b0cc73bbeacba35a',
 '0x5b613c8e3ca1e40d8c216158f0cfca8899e744c5',
 '0x5b76247e1fa700107d3eaf5ad4de09d0aca611bc',
 '0x5c7b561b1176f471abdf648deb75a8f3ce0fd0bb',
 '0x5c8dfbae712dd122979a0d68ce50c3e55dfbcdf2',
 '0x5d22f6d94b27cbc56e01fb8ce31e0374fc7519ee',
 '0x5d4621ef75c8ff5ecfedae7cffa34c6027244f10',
 '0x5e2d9c534870a686cf7d1dbb10f2b8b9a384bf29',
 '0x5eb2b16e1de28e6a8f8291ccbf9b9ae1b1384654',
 '0x5f0ffc1e29e9d9a3df918f7b0637db49c54feada',
 '0x5f1ddeac68b77626b754751676222aedfb3d7220',
 '0x5f60d6d8f21306f15f4f49c2a387a53ea523f9ed',
 '0x602fa030c301c97734970db71bd0c8437ad179d8',
 '0x60523efa6eefad0e2e93f6134313f4bf0b5b3dc6',
 '0x60a363530ec7db4fe74f5ebe62c337fdca8efe0f',
 '0x60ac80771b13e85dedac5a00044c09d9ebeb8b38',
 '0x60afed1a25888da89cc349c62ebe8aa8bb85be3a',
 '0x60d1df05426b3d7400db3aeda1824c287cf48bb0',
 '0x60e3049f07a95b86ec7a46f5774d5b28adf08e42',
 '0x6166d5f406745cfe2ff0a80310480a328bf726f8',
 '0x622a13dac538a0505bbdccb4f634a3acb949ac6e',
 '0x6239b06fe8aa9694ac99fc621fc787a1b60e436a',
 '0x62f6d496e22fee340074c5d46838772dc49624cd',
 '0x63741e82552c2796706f503ba6617213aadbd4de',
 '0x6516f67345e46f2c1a69d0ae8c8dcb8f245d5dae',
 '0x664dd5bcf28bbb3518ff532a384849830f2154ea',
 '0x665b835fdf8b546d0c5fe6757349f3413e009141',
 '0x679f0e4d00b1df0aca3f21f8064d3327a141adaf',
 '0x67acb2e127fdf171732b6b2648cb5c91c7db1843',
 '0x67cfcccaff0c00abe6a9b79d6fdf7e21ce02cae8',
 '0x695c505f3c4bedd5b83c3a0fbde731b7a7e8015c',
 '0x69e5a68a6ead1af1a52d1c2f4445f6abe046fe74',
 '0x6a61bd6d2c02c46e4b9b3342f3f6c62cc0e70c98',
 '0x6af699836704c73b645b5815c11d625efae3ee4d',
 '0x6b7a4166a06b988e90042f4259741b48870e1647',
 '0x6bcbc6fa460241ac1dfa7588160b51ff94f88733',
 '0x6bd9d0347e6a8f7e4abd80e1d9d2b4b26c5a935f',
 '0x6c1126d92032c2a52c6fc1e278dab5a5784c38dc',
 '0x6d11cbffe922454bcc8fd73252c444d9e38e2056',
 '0x6d12765d14a44e64c60dfe778c2ea8593a75373e',
 '0x6d2bdb4fc22dd43f2b9c1977851c5d234741e240',
 '0x6d430119898d851c25d84c0a0c14cd4b347374cd',
 '0x6e95d207d76a6217eb145316cb17132cf1cc1f42',
 '0x6ecf8f61ffdc46349a512c340e4aa2465ddd55f9',
 '0x6f3132060581c01eed77fb03ca3191d64280d173',
 '0x6f4cc8d64ed82bcb5a5394bfc9deb1cfba0bdcb7',
 '0x6fc2fc9cbdeeee283512c8bcb67784c26bb894f0',
 '0x6fc85efc3bbd758e832e18acc1b5e3fb7e2dc5bf',
 '0x701386193b756f4931f68881f536724a808cdcba',
 '0x709cc1ceb329eaf91f94f17e36528f984c717b66',
 '0x70a77ab3492da757aae4fbee03f8a14880523df5',
 '0x715e91b2b79a5644058a6174c7149c61a0778b72',
 '0x725d44b37a2865f9410aa6f6dc7d063e4a58b1aa',
 '0x72a1b7372a55e14ad8c4709d83c1a7799c8e5289',
 '0x72fc9b80cf03c71ecc5637123d73428088bd0f08',
 '0x73c0481d5eacdfc453ae9b2300490dc6abb078c9',
 '0x73d96e492c68c34bd34d4c18b42f4b98bbf7d18b',
 '0x74052fb4d5df7b18c3da6e529ecec84ee7cba8c6',
 '0x74d85b145a1a1531fb527add04d41018e12df746',
 '0x74f78b9f3c72f05d8a5c14df7896d24940e2c422',
 '0x756feeedd1a03fa3445da51593e445043e21e1a8',
 '0x75b5906a037aab387ac4c4d8e42926ec7c3d3571',
 '0x763444fe5a6995ce7a81473091b05d951b31c746',
 '0x767d222a509d107522e50161ca17ffcf0e5aa3de',
 '0x76819406044c555a9ad2f05376eb1abee36e286b',
 '0x77b6b8e00075f9519477062792c88a5b3f8a1a2e',
 '0x78249648311cf9f33848d897b4bc4c6e157cd3b7',
 '0x788939fc7a3407568638a25e9d71245482369ae2',
 '0x78c49ccba2527fc2da5d7d75b551b14563238c23',
 '0x798eb54aa861f83165c12f5774e8b34d179e7fc6',
 '0x7a08c2ed54af433710ba005689f0c729ec02e45c',
 '0x7b4860e56231abbaca6e2f7a2a86b476b610ff39',
 '0x7b520906313690f9b93e86bfb0e380ebb862c268',
 '0x7b867a8220043c142356695434e09e12f0f191c2',
 '0x7c224beeb6064d7ca376dc66a8d1245ad5926aa6',
 '0x7cfde52143b52f8d0f461bcc09d79b1e36bb6878',
 '0x7dfd727cc3bd475f4b2489c447a0bf5ba75c3e9b',
 '0x7e0922d50ac17a3643f196b0dc4d3639fa516b36',
 '0x7e86b2e9b9e6c0ee02b0200648d9fcf20557e3c5',
 '0x7ff2531f2f86c659b794b806f11a73eecb5d6005',
 '0x8024f47d8b554d267d1a70a056cd45f930f4d0a7',
 '0x805eec8e53f7986eec76db6783e8b76c6c8beeb4',
 '0x8071c5dc0a52cea323b7531f30500ce12abaa651',
 '0x81aa6141923ea42fcaa763d9857418224d9b025a',
 '0x81ce93120a781e094bcf7ba3383b9f0256e89ee2',
 '0x81ff7c3850da46fadd853904d7d4d5c31ddb2cb5',
 '0x8249a80ff06d321ea150b75dfa4d0775ba97e20a',
 '0x8277033efc826cb76deb7d78e325af5c4b84feb7',
 '0x827724446a3971dcdecf4302ca7adb14def086f8',
 '0x82a5fbc57eb2c7ba9db3fbd989f427b72ccaec5d',
 '0x83842eef993f4c25aa674f2a59c384467b7673e6',
 '0x8430adc8170395347bcd6c9945a09586a50456b9',
 '0x84e5c8518c248de590d5302fd7c32d2ae6b0123c',
 '0x8540f80fab2afcae8d8fd6b1557b1cf943a0999b',
 '0x857d5884fc42cea646bd62cc84f806aeb9a2ae6f',
 '0x85dae618f69cf79dfc36adb20145f575a01db94a',
 '0x85e9a235f911cd1593cc1f3e837ca5b005d5891f',
 '0x8765a1744f187561ad3e0466179d1356eae8e70f',
 '0x87aef945009c5ec80e941021bcccad6640065087',
 '0x87b9e4b8de86027ac02969dd3514b37af944a45f',
 '0x87ba3c38282409e6d13156303c43dd73b264010b',
 '0x87fd11b3fa60025862cb7004f19a34b2191970b5',
 '0x8814084562eb2f409a5d5a7db66c4ebd870849ed',
 '0x88a76452288266480e120eb10d8739148db85159',
 '0x88b629ade280df18180b31ad4bdbecaf6caa1827',
 '0x88dca8573a498425586b63ef15bea00cc9939ac0',
 '0x891c23d061e30b39398bfa24e22a6bbf324ab08a',
 '0x896afafba88e77b8c86a32fb2e84d93604545764',
 '0x89b537d4e0de035303dc1bdae18394f7a6c15c36',
 '0x89bab89465d515eb9b77f24e64e0708c8e76cfdc',
 '0x89c46f6bd6974aed96b074e34ad1eff003d5adf6',
 '0x8ac9a12a8723440c18e25dcbf8bb432b3325cfa5',
 '0x8b920b1287acaf78b1fcd993c9d3f23c97e0bd81',
 '0x8bee4f0d95283a80206ee69a4321888f2c2fb693',
 '0x8cba29dbec29c2458f29f50c1e2b9a909846f52c',
 '0x8d1b878509562fe8c097536e6e8da5bdeed05d1b',
 '0x8dbf0082b004e3ce72def7fb91e70243d20f4ca8',
 '0x8e4edb509043136af93bdaf68488e990c48b0077',
 '0x8e949b62a177452f5b327b539eaa63802a3ab6a4',
 '0x8ee23690145eb70498b4195558d7c6cdeca28128',
 '0x8f11a1f0c189347fb0479f84e8cd8b7dfbd52c7d',
 '0x8fbe9b006ec465eef78d3f8600eb006431989106',
 '0x8ff5d80aebff09b1d97f51e55a4b8dc4fb4d82aa',
 '0x9007d299738eb83d35621676d44d327dececf82d',
 '0x90111e5eff22ffe04c137c2ceb03bcd28a959b60',
 '0x90a4e1e0c3b3503c758ab487b8bc06fa730cdaf0',
 '0x90fdeaa5fff137bcbdee150fbff5b556dfc23ab3',
 '0x91724b63dc4e723609f3e0faca1b0e7b78579c47',
 '0x918137350cd792132117689ff0361eeebbe69cfd',
 '0x920855526012c5161e5b4dd90a7986dfb88e24c5',
 '0x927521baeba66f707a77b91910a84ff5ccf3447a',
 '0x930a7cd60a633128b7c5181307781e6d033ba51a',
 '0x934a3231e52875ae84fb3e6c6c42f8849bca3530',
 '0x935ae103195931acb7865bc75c20b15778a372fd',
 '0x935d42dee1836adf6793bd7dae796ee3d96d0eee',
 '0x93ce3113649003952df881248e84964283770b80',
 '0x945191ab90d5b511f80c297681e5de54e55c50b8',
 '0x9471f70f2518846f7a076636d64e5a22787da105',
 '0x94769999528f0a9c40cb0c9246562293c12b1681',
 '0x95477551b2a5b5dedf7c260904ec19dc2f432a6d',
 '0x954decdcd4ff4ee72fdfe06eb4a0688b590a9453',
 '0x9567963a5439cb8740dd2f20bcdd5eed288beb7f',
 '0x9599f0512efc9eb1f88c8197fa2b487bcec571fa',
 '0x9608d122fee7381729892e29a8fb091793268d21',
 '0x962699db05a9334c5cd1f9c2867d5160c8e37742',
 '0x9751d3216f5f389c2d2341e6af5fa0da9b685b59',
 '0x97a349bd702512599144b61f873c4dcc04af1cd8',
 '0x97aa869e59f62b511bea0a1de61b4d67d92e0de2',
 '0x983563f06b8edc6c1132a91aac6454cc4bd9b100',
 '0x991f3775c81d6f8331b9a812eda34ea48a7ea76d',
 '0x9986eca64c1d00b9aab93507cf955232480d2584',
 '0x9a517b5d1fea6e42d50e711fa212fa8121c1f939',
 '0x9ab119acbfc335ef4bd0d0bb0cc57bdaf92dd3a2',
 '0x9ac1ed9517c7a24c745c2b7e7fae95595fa2f7ec',
 '0x9b0566e1cb77899a5b6c56f12ed4496e4c19356d',
 '0x9ba5c3e4f8f841588dbfd3303cd96987f1a8edbb',
 '0x9bb4615a1c88a65dac9ca09d21e89b3543d291e8',
 '0x9be426c8a28ee7ca935b5c27a4bc2395640c9378',
 '0x9bff7b87d39b6799f3c5efcdfd9e124b838ba9f8',
 '0x9cd34446ca93be137ad7beda6af5957d79b83851',
 '0x9cdc00b1c9fcc2450af0562855580605909eaed1',
 '0x9d576ac210f3d07a3302d1eaf171663ad8fc8ee2',
 '0x9e99c6ada8c9a1b89df77ace103f8aa068593012',
 '0x9ec162ea326f93c81fb3790eafb2f049af800b4d',
 '0x9f759df1d2a6bbfbea17fb96bd3967a1b159b737',
 '0xa02d542bee5e859caa7d6df03fce3c7383ceb6af',
 '0xa07feb22cd2cec2b8d9fda1e4d1a84d80762981f',
 '0xa0f39111d7d1124aca553e53883ea4d991a80675',
 '0xa1569acb1c22b5479fd1a190b4d5867851d916fb',
 '0xa18fb9312ef2d98219f169653d8ad9e21df1fabc',
 '0xa1b17041306ff5510a9ded58040005d22a296abd',
 '0xa2c917c5e02afc7740db0ac06c6df2a3b3b5b458',
 '0xa2ef5afd8f2fc6c70a4e1eb09986a683f6d3179b',
 '0xa335ade338308b8e071cf2c8f3ca5e50f6563c60',
 '0xa3a2a065ba87ec0c6881027daecd7b086328d363',
 '0xa401dd87d2e6ce8acc98653f8ebc830655aff87f',
 '0xa4116557a0055eda4c192edc4785c02414c4c264',
 '0xa4c83c3053376e9ce06c05032c6a758c235a5d1a',
 '0xa6e1c5b55b6be38df3c96473974d135cd280e3e9',
 '0xa7525608b6bbb47f4bbb5760ad7ebf3372bc5fed',
 '0xa75f9c8246f7269279be4c969e7bc6eb619cc204',
 '0xa808ba63710fb2f052871eddd6ac7f453df609ae',
 '0xa8204bef9286cc30cb2c4c879d17555bad2928b7',
 '0xa88056beee1d5c3b0990003e0a6d699c6e351451',
 '0xa8fc02148e3c3a642340a60742a6992682981b50',
 '0xa91c2ceb9d2e343bfd5a12d5b3b3794346a8c473',
 '0xa93cf81692bc895a3d1f2198f2617ebded589cc1',
 '0xa98040f59d6db9a94c5ce78bce7d6d4637e81cd8',
 '0xa9dc457d2c008a8d9fc9deaeae478e8f87400466',
 '0xa9ea51277c04c083ce63f3d11b63bbce215faba1',
 '0xaad6081085ff6bed7f9ff2f697c99934fba44c61',
 '0xab29c783672a4844ea3ab81bc36205e7fca243df',
 '0xab4382aadae5bf4b37b90b9dc07fc72d52e2a28a',
 '0xac4bd05953587836dfb12843a9951570ff403c0f',
 '0xaccc4efb9b6462e7bd206a009fd3c436b0081d80',
 '0xacd3f8c88ff24a85bec668f6c8e7898d8cccbad8',
 '0xadee949d4bc54badf9bc7f2f8cd236383d82b413',
 '0xae6f85921273599c5c2469c7d5af4132ae6e079e',
 '0xaf66285d26d1591f37fd6ce628a8a3003780c828',
 '0xafa32b3cdf8bed419a92724153feb55173e11968',
 '0xb009e0cd0af8025afc880d2552eb4ef1afa73bc0',
 '0xb051e4eb23c59987acba926207b0d5a9fa243046',
 '0xb13c38ddcf7afb7b60cb5ce7d1208e4b32d8057d',
 '0xb262b5955bf79f0b1c5fe45c88c90f0ec9f4af53',
 '0xb2f56241b95dd591f1e4d1899eecd455837f3408',
 '0xb2f6129b4b2fa2061bbf6d136bee016a66d821fb',
 '0xb394f1aa30ba874df3ae6097bf4c2474b2d8f3ac',
 '0xb43eebac012cb2f12e1ec258a6ece20a7aa4712f',
 '0xb44373deb287e83ba5fd8909f4076c9b9ccf0ec4',
 '0xb45e2b252969394a48e46616378f19b1f1f32bdd',
 '0xb4a86fc9be9789cbed6b23c2b41fc01d5b3bef0e',
 '0xb4b04564f56f4795ea4e14d566af78da54a99980',
 '0xb4c0d18ccaa196631f66bd4a7ff53b1c14379b43',
 '0xb4d8eb807b0e8e2b9be412cff9dda6f793d2c6d0',
 '0xb54dc826b9c0e2407a9c6e020b6e25fe88112052',
 '0xb5a2b7409aa016fd68a1bc1c26fb3b68f7a9ee2d',
 '0xb62ce87b2e18a3c85666da2a7970032f433d843f',
 '0xb68ec411dbf0327a72e31fade83992e3fd929b93',
 '0xb6f8685648171ee510d9190c71aac891f96731a8',
 '0xb728d59914bbce515957aa320315254f0377bdbc',
 '0xb730d3908b9b83ac4d876ae5c70aa9804f39694a',
 '0xb7e3fb83555089b5a33ba7cf5a1110cb40f8310a',
 '0xb81b552fdb011de002c2c09e7a63604e768ebcc8',
 '0xb8c30017b375bf675c2836c4c6b6ed5be214739d',
 '0xb8e83bd6f2c956c1df7aa33e9a5ebf5869c8537c',
 '0xb92c8ed1bc3a57928e5e5ac229842f3270984155',
 '0xb9c5629971060aaf9858a54f70a50c74f941b630',
 '0xba9be4236bf5ee96d569937bdd4fa92f1a568a21',
 '0xbafcb99bc0ca6a079acd94d4bb43f784ea762d15',
 '0xbb36ccd6373b94e713ebe942816170997b022525',
 '0xbbb1c9a4ea0c16069364948e4002d3a7361358d5',
 '0xbbb6ef032838fbd280849e7f5f6df326860e6f6b',
 '0xbbdf63e9f762ae90acf96f01c11106b812973001',
 '0xbbe844467051fe04cce050efb42cf824431d1e52',
 '0xbbe8e2ea7173095325034beb7f44abecc54cccb9',
 '0xbd356a9c20771d2be448bc7a556cfc0930c726fd',
 '0xbd5975d969a5590b663c329490add6030c28a9ae',
 '0xbdbf8144b55354ca415c9f6e4b1f832d146875b2',
 '0xbdf7b52f67b014364bcdc45efe6f0ccd710d4f43',
 '0xbdfa4f4492dd7b7cf211209c4791af8d52bf5c50',
 '0xbea1771efed9d4a80d6ce19aedb70e56dd739b49',
 '0xbec072be7d929026fcd3384192120916515d9360',
 '0xbfb08cde8c6f49f333f1860ae00d9a987443ea27',
 '0xc04bc1996320f27c0a6018cb370c9469a9dd3a4c',
 '0xc09ac4d550474c8b2259a188431e6bac7ec1a698',
 '0xc0a4352241f4efbad1a919398ad1f77bd591c5de',
 '0xc0dcc094f370bbc6ecc832f6196136437f458f74',
 '0xc12ca084236a042a658c28c894df95e3b80de125',
 '0xc13c37c6a3b077ef147c750a310cde3635ac7c49',
 '0xc1b55a0ebbc527a03b52541d5c38c14571b04cfa',
 '0xc21ab17be2bab6d8456eee72439e9b3d569c7c5d',
 '0xc2254206edb9f55eef46dca0e85f5b8cbcd2bb91',
 '0xc2554fd4e06826460998f9cb7f10dc10e2450f22',
 '0xc2efbb59f6679920acc462e83c8969b691b9cdf1',
 '0xc2fb837914b078e658b84eecb37301637c3a7134',
 '0xc30231807c6adad9ed6b8e71781208af6dcd42d7',
 '0xc30eb1798b9479c4feea87cf70996e8379ff3554',
 '0xc35b8f936a4467989c33b4febecb923efc38c403',
 '0xc36f810582ce3a4a2b7b2e1d523e216f887fb593',
 '0xc3b06959e7ab78adf39f143ec479596d04157567',
 '0xc3c5ac9c328323e53dbdf064d94779436b91c49a',
 '0xc423875b56dcedb6e84c744f695c59c97ab0cf2e',
 '0xc4ed448e7d7bdd954e943954459017be63584f69',
 '0xc54e01eaac24a582b3d4ecb66a1657462be98f85',
 '0xc5a568896e57d513fdb3b88356f71213866bc797',
 '0xc5c5b53438a7fc9cddea4f0ded2d12fbf75b6c76',
 '0xc6d9ef4a0d637992ebae308639e1074abff917eb',
 '0xc6f71455022b53cabb8f3facc4bf02bbf745a26b',
 '0xc71a98a26d839e6606d60cabb3cf23ccdb500140',
 '0xc75351e058038dfb1336e65eef37ff298e524513',
 '0xc77fa6c05b4e472feee7c0f9b20e70c5bf33a99b',
 '0xc7f651ba6e744c854aa87bc39d4cdd653f942386',
 '0xc89c168138d3c666bc5c5a85cbb7e491b0d540ac',
 '0xc95932d5a11ecb8eb776ee4ef062888008e9b84d',
 '0xc9a31d9f064060587a503b03accdd9f8faaabdb3',
 '0xc9a9b8163ff0f024d16ced23c16ffb764d72ba21',
 '0xcacc6c1f624289d0c4e98a6552b51cc162a3e90c',
 '0xcb4d38e12cebccb0c15b9b660babae7b9494e8f6',
 '0xcb8b4f0b21d17127ac515c9eb58fe50ca54a7161',
 '0xcbba4da463eef7c29e4f18ac776900adaa9ad1ab',
 '0xcc2b2295ca9e2b8513d549b54df1d8fb9072f4b1',
 '0xccadda2ba47263f2d22f4a27a7435f8463c17b79',
 '0xcdd164ed67987ac6d00292f1903d836bb514d084',
 '0xce313ee763b689379dc2f51cf31cd8fdb1930c1c',
 '0xce4e1fa964ece5eff151223419747b86743e88d8',
 '0xce6208894bcc98c9b00683a5676fd98c9746416e',
 '0xcffce90b8b88313d053bb6170517beb18cebaf3e',
 '0xd17c048831792862b4826cbbf733dcaa23a3a16b',
 '0xd196913d6f5ce8a29fa2acb375910fa6982a31d5',
 '0xd19761b428cf5fc57b6c38c862396e0a7453d722',
 '0xd273e3a1eadead918a01123e7b9ebf20ace3fab4',
 '0xd314d0f4278098ff5772ebbb3d9b5a42dd8349d8',
 '0xd3a543a98492dc2bd7e88f222a60ead118e62184',
 '0xd45b4944955e480448ecd7696cf2aa7a4c420448',
 '0xd47e9aafdcb307f825a1e7c1f015cefb732054a6',
 '0xd4a4d7a4ac2c705a4f5afaa9536cc89d0682256a',
 '0xd6516c877bc01c03d4bee656a29ca7fc81491a3c',
 '0xd6c413f42b8e670f1292446f2c711336cd272003',
 '0xd778555afa02af57f077bd48b1204c5405d28887',
 '0xd783947ce4924147f35b319bd247ee628e7fb0be',
 '0xd8680b048e3f417433f587320850a310ff92759b',
 '0xd876c98ce1f63d3822c783d8aad55ca5a8e4e2e8',
 '0xd8bf2e630329807483327c5c089cbaad3f846206',
 '0xd8c7c4453232c4ee5389e4a3ad8391d6b671afb5',
 '0xd97ce1eeda55e8aadb57b5e619cc92ad600f83c5',
 '0xd9d4abd0b72099481f6c1c0041190b997a707abd',
 '0xd9e08d7965df0c3f974b7da942c262ddd207fb28',
 '0xda015d7b426755d7c28a8069f1c94321b5e70143',
 '0xda223731dc769f3d704063c6104bfd7372dea5a7',
 '0xdab264328d15372325ff6783dc14114ebe042ce4',
 '0xdae7d1ecf079c822e269f15134da59c8c2a26503',
 '0xdafc095d560c544d5d37dd4006c87d22fc4f7339',
 '0xdb1c4f958d2e65639cf4607741a6f8a2c7b928ca',
 '0xdb97aa9b0c07254ef9e017641f5da271e5c31f35',
 '0xdbf5e9c5206d0db70a90108bf936da60221dc080',
 '0xdc830b4994c01f6bb9e0b4465081fd88c2e05d2c',
 '0xdce2ac75bbdb26ccd48199dae80f1b58965509f0',
 '0xdd23abb2227b4a3add86051810e03791f41c34e4',
 '0xdd2ba36f0ae4d0f8c9cd6af6006f9d4e9aab8745',
 '0xdd2c7bbc07f51820e7d44601ed6467a2d32369fa',
 '0xdd4d11a97a69d976535d588209e2cd80b116e393',
 '0xdd5fa5909a02555e865bbd84dfdc59c36c160649',
 '0xdd92d3d535734850bad08b105ea16586b294032f',
 '0xddbc886f9f82ed1a89544620136102676830524a',
 '0xde654740ec9d0ad6d9fc85ebf813a77a7a7719b5',
 '0xdec2d9d0aaabb2a70b96a433328ccdf6c24199b6',
 '0xdf4da9ac4d2d326c7162165cfc276607e1d63b10',
 '0xe020386c6954d328b1202336817b0383215d2b62',
 '0xe0a82d0e3fc587560edab27891a6a4080b91e137',
 '0xe0dde603f2e13b7d63508c7296b9348bbb40df02',
 '0xe12c95faf4656bb4482a9a840901d688f90bfe72',
 '0xe1a655553ce22e454c9d474dc3c3b41d4fc0b191',
 '0xe2144d44fc5c33563b69e2fa62506dbc2d795fed',
 '0xe27e7c50773ca859875107ef7db5e22aa2e248fd',
 '0xe2e4f2a725e42d0f0ef6291f46c430f963482001',
 '0xe2f4711f617714e18af6ed3d7ba58923bfe4b238',
 '0xe30ac711b67437b8f223d82c9ed19c0b2fcf92a5',
 '0xe3512e0bf0b2acb7518a4edddab598425c90633b',
 '0xe3b0f7aaba333929d6c76d4602ee11d88d61f40f',
 '0xe3d427848f6efc437a8451de24c10e6c534274b3',
 '0xe3f928cdf952e94754bb7580d16e4105cc5b9dd0',
 '0xe45b178819526d1b5ae56bb0db182a9aa2fe5752',
 '0xe49c9f7308404c1630129513c8d0da5cfec8e854',
 '0xe4ac8a1be6c373b300f46fab9e360865e65ffda5',
 '0xe5350e927b904fdb4d2af55c566e269bb3df1941',
 '0xe60b7bccd57d50ca2cca46e4f977688c91ab0d79',
 '0xe65a506493bb04c1d20b2fbe01de9dc163c065bd',
 '0xe732d91870da0b0bab3d61a6de8b4e61a9a96ff4',
 '0xe800fe8345143bcb76c4cddb71de02fa79097217',
 '0xe8342f3f61e8fdb281061a79506ba4f39ad32c0b',
 '0xe93381fb4c4f14bda253907b18fad305d799241a',
 '0xe9404dc46cb03e1ce11252e2b3e6c0efb98a34d6',
 '0xe9a02dd5c2ac0ec432fac217ce709394b297a28a',
 '0xe9c235b9beefbe2320e23ed97ed8bdd1905b86e3',
 '0xead3bb55a50af1a94a125b87d964060046a394e7',
 '0xeaf24ff86b12e949dac584cfcd82f62fb8b96260',
 '0xeb0c78d34e3eefa3483ac3a3a1397a496d592ca8',
 '0xeb2629a2734e272bcc07bda959863f316f4bd4cf',
 '0xeb5b6185b4e5bc9b3a1190be8ffdae7475e76e89',
 '0xebb13e21fb572469ecfab09034051b855b901d63',
 '0xebe880a7bd376e9f1e3e4ac6fec2744d4b858770',
 '0xebf442a15094289f7483c1a9d12367fc1531c4f6',
 '0xec9423970ccf2f3deac15aac8b9d310f544d01e5',
 '0xed01508f9071cf7e6e33ca4a488b946938e92384',
 '0xed04d3792c439b8af827b3e46ee626827de53db5',
 '0xed8b99113ffdc27a514a9e1208e660149e850b65',
 '0xed997fef3cb3c2b8f56f1116ddac349b8e73ac7f',
 '0xede040a7e37c6eaa3a6e0dbf4b60a4b729b84741',
 '0xee23f4bc1671d048a8e592aabd0b2be497bcb5c2',
 '0xee9a0ef4ce0ab1b11d8ce00f0e4520b9f5a116d6',
 '0xee9f9641715d06af257ec7377b318fe33392e8be',
 '0xeeb009194435c51e1d2e1c8c424edcb0ddeb7723',
 '0xef764bac8a438e7e498c2e5fccf0f174c3e3f8db',
 '0xefb3fa9759cdaa2c47903019ba26cb822776b240',
 '0xf0a5293b7282c0407b04fcf15b5d64db0ff3d2f3',
 '0xf0bb3b93552edf481a54b9e3937ad8ebcde892f1',
 '0xf0dba406d95115e69f339fd76f194a85ae441f6e',
 '0xf0e2c7e7266fb19f8a4118670ce50e95c4c87790',
 '0xf128177634f2a9e74658dbfe74d9ddb0f2d24f3d',
 '0xf14cfa45bd376a080f1326d3c9edd753dd9d6cab',
 '0xf28778f08dd8809166219952061de681c6a9910d',
 '0xf28c45a326bef209b26642c67cb3b9d093031201',
 '0xf3147df6b04323aecdf891463827b9ff2f4ff111',
 '0xf33fcc4ecc62193029a142c77611b7a10a5ce744',
 '0xf45f7d6cc1d79dd677c3e976711cf29fc306f929',
 '0xf4ae81d51f617065bf952bdc8452029c1d817800',
 '0xf55777a6be6c9b0fc06cc28486751672352c212f',
 '0xf55a646dc8302cd5cac290ebefec97853f88967d',
 '0xf5b0af852e3dedc03b551f7050b616b5c77c7645',
 '0xf5b2217b3da10661c07f77e0ad4bae72e840a498',
 '0xf5dd76a75d2872c14e718a020a2bbdad4f5d8cfb',
 '0xf5fe364d18f4a5a53badce9a046ba74cfc97f6fb',
 '0xf61a81edb2b572e791c8820d329488e276b7104a',
 '0xf69dcb70ad643c520e9c5ef96dceb3262867eaee',
 '0xf75fcd9849d3365d436d0cd889ed500150c9482a',
 '0xf789c601625e2a24ebfc96903e2b91105494526d',
 '0xf78fe6824f08aff7cca44ce89c2a3c07a06e234e',
 '0xf79bb3c50bb6ca236fb56aadfae2e5ad6f3cb807',
 '0xf908ccbf1e1b30aea58043e44ade5db6c3f2e3ed',
 '0xf9421d75a2ce50ac11ff438cae33813db81ae852',
 '0xf942886761950188633f168989341e181af777c5',
 '0xf973958c45d231317138fcb6f28ef9d6e756fa80',
 '0xfad8a0509c9f8ba17e89869f929ba84b7e7cb5fa',
 '0xfb5b7d1691a9235d6e58b5002590229f30ec7f1b',
 '0xfb71b66c559c9aef0fc338da257f178e8a3e6601',
 '0xfbf75933e01b75b154ef0669076be87f62dffae1',
 '0xfbff0486168361e92b071c901500b3c1e483b684',
 '0xfc57fdfec1758353222f5fce428bed2aeccf3ad7',
 '0xfc6aeffa0097eacfefa983b006ef06833567707d',
 '0xfd125fd8d601d1363514e535fd8f585881df8cbc',
 '0xfd82a64f17d681b6675a7c1987fbea8c11031981',
 '0xfddba294017fef1f221ff80cae07cb214f744c28',
 '0xfe6f8b49f6fc5a02629c5f57915d2a154e252857',
 '0xfee5f64c87eec05e83de4ca73534484066f9c5c7'}



def fetch_all_contracts():
    with Session(engine) as session:
        for address in session.query(
                Address
        ).filter_by(is_contract=True).all():
            CONTRACT_ADDRESSES.append(address.value)
    # CONTRACT_ADDRESSES.remove(CTX_ADDRESS)


def calculate_stats():
    fetch_all_contracts()
    output = open("address.xlsx", "wb")
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet("Addresses")
    row_counter = count()

    with Session(engine) as session:
        addresses = session.query(Address).filter_by(is_contract=False).all()
        with workbook:
            worksheet.write_row(
                next(row_counter),
                0,
                [
                    "Address",
                    "No Of Holding Days",
                    "Actual Balance",
                    "Staked Balance"
                ]
            )
            for addr in addresses:
                address = addr.value
                if address in suspicious_addresses:
                    continue
                events = session.query(TransferEvent).filter(
                    # get rid of this filter
                    (TransferEvent.from_ == address) | (TransferEvent.to == address)
                ).order_by(TransferEvent.timestamp).all()
                for event in events:
                    _datetime = datetime.utcfromtimestamp(event.timestamp)
                    amount = event.amount / 10 ** 18
                    if event.to in REWARD_HANDLERS + TREASURY_VESTER + [
                        CTX_DEPLOYER, DELEGATOR_FACTORY, TIMELOCK
                    ]:
                        # ignore CTX owned addresses
                        continue
                    elif event.to in DELEGATORS:
                        # increase staked balance, decrease total balance
                        TOTAL_BALANCE[event.from_] -= amount
                        STAKED_BALANCE[event.from_] += amount
                    elif event.to == SUSHISWAP_CTX_POOL:
                        # check if swap, mint or burn
                        is_swap = session.query(session.query(SushiSwapSwapEvent).filter_by(
                            tx_hash=event.tx_hash
                        ).exists()).scalar()
                        is_mint = session.query(session.query(SushiSwapMintEvent).filter_by(
                            tx_hash=event.tx_hash
                        ).exists()).scalar()
                        is_burn = session.query(session.query(SushiSwapBurnEvent).filter_by(
                            tx_hash=event.tx_hash
                        ).exists()).scalar()
                        if [is_swap, is_mint, is_burn].count(True) != 1:
                            continue
                        if is_swap:
                           ACTUAL_BALANCE[event.from_] -= amount
                           TOTAL_BALANCE[event.from_] -= amount
                        if is_mint:
                            SUSHI_STAKED_BALANCE[event.from_] += amount
                            TOTAL_BALANCE[event.from_] -= amount
                            STAKED_BALANCE[event.from_] += amount
                        if is_burn:
                            TOTAL_BALANCE[event.from_] += amount
                            if SUSHI_STAKED_BALANCE[event.from_] > amount:
                                SUSHI_STAKED_BALANCE[event.from_] -= amount
                            else:
                                ACTUAL_BALANCE[event.from_] += (amount - SUSHI_STAKED_BALANCE[event.from_])
                                SUSHI_STAKED_BALANCE[event.from_] = 0
                            # case where amount received after burning is
                            # more than staked
                            if STAKED_BALANCE[event.from_] < amount:
                                STAKED_BALANCE[event.from_] = 0
                            else:
                                STAKED_BALANCE[event.from_] -= amount
                    elif event.from_ in DELEGATORS:
                        # reduce staked balance, increase total balance
                        TOTAL_BALANCE[event.to] += amount
                        STAKED_BALANCE[event.to] -= amount
                    elif event.from_ == SUSHISWAP_ROUTER:
                        is_burn = session.query(
                            session.query(SushiSwapBurnEvent).filter_by(
                                tx_hash=event.tx_hash
                            ).exists()).scalar()
                        if is_burn:
                            TOTAL_BALANCE[event.to] += amount
                            if STAKED_BALANCE[event.to] != 0:
                                # case where amount received after burning is
                                # more than staked
                                if SUSHI_STAKED_BALANCE[event.to] > amount:
                                    SUSHI_STAKED_BALANCE[event.to] -= amount
                                else:
                                    ACTUAL_BALANCE[event.to] += (
                                                amount - SUSHI_STAKED_BALANCE[
                                            event.to])
                                    SUSHI_STAKED_BALANCE[event.to] = 0
                                if STAKED_BALANCE[event.to] < amount:
                                    STAKED_BALANCE[event.to] = 0
                                else:
                                    STAKED_BALANCE[event.to] -= amount
                            else:
                                if LAST_HOLDING_DATE[event.to] is None:
                                    LAST_HOLDING_DATE[event.to] = _datetime
                        else:
                            raise Exception("Unknown SUSHISWAP_ROUTER Event")
                    elif event.to in CONTRACT_ADDRESSES:
                        # exclude contracts from distribution
                        continue
                    elif event.to == address:
                        # adjust both to and from balance
                        # increase balance
                        # check and set last date
                        ACTUAL_BALANCE[event.to] += amount
                        TOTAL_BALANCE[event.to] += amount
                        TOTAL_BALANCE[event.from_] -= amount
                        if LAST_HOLDING_DATE[event.to] is None:
                            LAST_HOLDING_DATE[event.to] = _datetime
                    elif event.from_ == address:
                        ACTUAL_BALANCE[event.from_] -= amount
                        TOTAL_BALANCE[event.from_] -= amount
                        if TOTAL_BALANCE[event.from_] <= 0 and amount != 0:
                            try:
                                TOTAL_HOLDING_DAYS[
                                    event.from_
                                ] += (
                                        _datetime - LAST_HOLDING_DATE[event.from_]
                                ).days
                                LAST_HOLDING_DATE[event.from_] = None
                            except Exception as e:
                                continue
                    else:
                        raise Exception(f"Unhandled Case: {event.id}")
                if LAST_HOLDING_DATE[address]:
                    TOTAL_HOLDING_DAYS[
                        address
                    ] += (
                            locked_date - LAST_HOLDING_DATE[address]
                    ).days
                if ACTUAL_BALANCE[address] > 1 or STAKED_BALANCE[address] > 1:
                    if ACTUAL_BALANCE[address] == STAKED_BALANCE[address]:
                     continue
                    print(f"{address}, "
                          f"{ACTUAL_BALANCE[address]}, "
                          f"{STAKED_BALANCE[address]}")
                    worksheet.write_row(
                        next(row_counter),
                        0,
                        [
                            address,
                            TOTAL_HOLDING_DAYS[address],
                            ACTUAL_BALANCE[address],
                            STAKED_BALANCE[address]
                        ]
                    )

        output.seek(0)
        output.close()


if __name__ == "__main__":
    calculate_stats()
